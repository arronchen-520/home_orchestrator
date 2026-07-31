import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from board_graph import BoardService
from models import AgentReply, CaptureAnalysis, ItemDraft, QueryPlan, RouteDecision
from test_support import TestBoardDatabase as BoardDatabase


class BoardContractTest(unittest.IsolatedAsyncioTestCase):
    def database(self, temp_dir: str) -> BoardDatabase:
        database = BoardDatabase(Path(temp_dir) / "board.sqlite3")
        database.setup()
        return database

    async def test_every_message_is_routed_and_capture_uses_reminder_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = self.database(temp_dir)
            lin = database.add_member("test-family", "Lin", "Parent")
            sam = database.add_member("test-family", "Sam", "Driver")
            route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="capture")))
            capture = SimpleNamespace(
                ainvoke=AsyncMock(
                    return_value=CaptureAnalysis(
                        status="review",
                        message="Please check this.",
                        items=[
                            ItemDraft(
                                kind="event",
                                title="School pickup",
                                start_at="2026-08-01T15:30:00-04:00",
                                reminder_at="2026-08-01T15:00:00-04:00",
                                remind_member_id=sam,
                            )
                        ],
                    )
                )
            )
            with patch("board_graph.router_chain", return_value=route), patch("board_graph.capture_chain", return_value=capture):
                service = BoardService(database, "test-family")
                response = await service.message(
                    {"text": "School pickup Saturday at 3:30", "actor_id": lin, "timezone": "America/Toronto"}
                )
                self.assertEqual(response["intent"], "capture")
                self.assertEqual(response["status"], "review")
                self.assertEqual(response["drafts"][0]["remind_member_id"], sam)
                route.ainvoke.assert_awaited_once()
                board = await service.confirm_capture(response["session_id"], lin, [sam], [False])
                self.assertEqual(board["items"][0]["remind_member_id"], sam)
                self.assertNotIn("owner_id", board["items"][0])
                self.assertNotIn("assignment_state", board["items"][0])
                await service.message(
                    {"text": "Buy milk", "actor_id": lin, "timezone": "America/Toronto", "session_id": response["session_id"]}
                )
                next_capture = capture.ainvoke.await_args_list[1].args[0]["conversation"]
                self.assertIn("Buy milk", next_capture)
                self.assertNotIn("School pickup Saturday", next_capture)

    async def test_query_is_read_only_and_keeps_one_conversation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = self.database(temp_dir)
            lin = database.add_member("test-family", "Lin")
            database.create_items(
                "test-family", "seed", "Pay bill", "text", "UTC", lin,
                [{"kind": "task", "title": "Pay hydro bill"}],
            )
            route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="query")))
            planner = SimpleNamespace(ainvoke=AsyncMock(return_value=QueryPlan(sql="SELECT title FROM items")))
            answer = SimpleNamespace(ainvoke=AsyncMock(return_value=AgentReply(message="You need to pay the hydro bill.")))
            with (
                patch("board_graph.router_chain", return_value=route),
                patch("board_graph.query_plan_chain", return_value=planner),
                patch("board_graph.query_answer_chain", return_value=answer),
            ):
                service = BoardService(database, "test-family")
                first = await service.message({"text": "What do I need to do?", "actor_id": lin, "timezone": "UTC"})
                second = await service.message({"text": "Which bill?", "actor_id": lin, "timezone": "UTC", "session_id": first["session_id"]})

            self.assertEqual(first["session_id"], second["session_id"])
            self.assertEqual(len(second["messages"]), 4)
            self.assertIsNone(database.get_board("test-family")["items"][0]["completed_at"])

    def test_today_combines_happening_due_reminder_and_overdue_without_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = self.database(temp_dir)
            lin = database.add_member("test-family", "Lin")
            event_id, due_id, overdue_id, reminder_id, recurring_id = database.create_items(
                "test-family", "today", "today", "text", "America/Toronto", lin,
                [
                    {"kind": "event", "title": "Dentist", "start_at": "2026-08-01T15:00:00-04:00", "reminder_at": "2026-08-01T14:00:00-04:00"},
                    {"kind": "task", "title": "Pay bill", "due_date": "2026-08-01", "reminder_at": "2026-08-01T09:00:00-04:00"},
                    {"kind": "task", "title": "Return book", "due_date": "2026-07-31"},
                    {"kind": "task", "title": "Pack bags", "due_date": "2026-08-03", "reminder_at": "2026-08-01T18:00:00-04:00"},
                    {"kind": "event", "title": "Weekly swim", "start_at": "2026-07-26T10:00:00-04:00", "reminder_at": "2026-07-25T10:00:00-04:00", "recurrence": "weekly"},
                ],
            )
            summary = database.get_today("test-family", date(2026, 8, 1), "America/Toronto")
            by_id = {item["id"]: item["today_reasons"] for item in summary["items"]}
            self.assertEqual(set(by_id), {event_id, due_id, overdue_id, reminder_id, recurring_id})
            self.assertEqual(set(by_id[due_id]), {"due_today", "reminder_today"})
            self.assertEqual(by_id[overdue_id], ["overdue"])
            self.assertEqual(by_id[recurring_id], ["reminder_today"])

    def test_follow_up_notes_are_append_only_and_tasks_use_completed_at(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = self.database(temp_dir)
            lin = database.add_member("test-family", "Lin")
            task_id = database.create_items(
                "test-family", "task", "Call school", "text", "UTC", lin,
                [{"kind": "task", "title": "Call school", "remind_member_id": lin}],
            )[0]
            database.add_item_note("test-family", task_id, lin, "Left a voicemail")
            database.add_item_note("test-family", task_id, lin, "School called back")
            database.update_item("test-family", task_id, lin, {"completed": True})
            item = database.get_board("test-family")["items"][0]
            self.assertEqual([note["content"] for note in item["notes"]], ["Left a voicemail", "School called back"])
            self.assertEqual(
                database.query_assistant("test-family", "UTC", "SELECT content FROM item_notes ORDER BY created_at"),
                [{"content": "Left a voicemail"}, {"content": "School called back"}],
            )
            self.assertIsNotNone(item["completed_at"])
            database.update_item("test-family", task_id, lin, {"completed": False})
            self.assertIsNone(database.get_board("test-family")["items"][0]["completed_at"])

    def test_recurrence_remains_event_only(self):
        with self.assertRaisesRegex(ValueError, "Only events can recur"):
            ItemDraft(kind="task", title="Trash", recurrence="weekly")


if __name__ == "__main__":
    unittest.main()
