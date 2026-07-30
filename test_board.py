import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

from board_db import BoardDatabase
from board_graph import BoardService, ExtractionResult, ItemDraft


class BoardFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_domain_items_persist_without_graph_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.sqlite3"
            database = BoardDatabase(path)
            database.setup()
            service = BoardService(database, "test-family")
            board = await service.execute({"type": "add_member", "name": "Lin"})
            actor_id = board["members"][0]["id"]
            extraction = ExtractionResult(
                items=[
                    ItemDraft(
                        kind="event",
                        title="Dentist",
                        start_at="2026-08-31T15:00:00-04:00",
                        recurrence="monthly",
                        monthly_on_last_day=True,
                        recurrence_until="2026-11-30",
                    )
                ]
            )
            with patch(
                "board_graph.parse_with_openrouter", AsyncMock(return_value=extraction)
            ):
                board = await service.execute(
                    {
                        "type": "add_item",
                        "text": "Dentist every month",
                        "actor_id": actor_id,
                        "timezone": "America/Toronto",
                        "source": "text",
                    }
            )
            event_id = board["items"][0]["id"]
            await service.execute(
                {
                    "type": "update_occurrence",
                    "item_id": event_id,
                    "occurrence_date": "2026-09-30",
                    "actor_id": actor_id,
                    "fields": {
                        "title": "Moved dentist",
                        "start_at": "2026-10-01T16:00:00-04:00",
                    },
                }
            )
            await service.execute(
                {
                    "type": "cancel_occurrence",
                    "item_id": event_id,
                    "occurrence_date": "2026-10-31",
                    "actor_id": actor_id,
                }
            )
            database.close()

            database = BoardDatabase(path)
            database.setup()
            self.assertEqual(len(database.get_board("test-family")["items"]), 1)
            calendar = database.get_calendar(
                "test-family", date(2026, 8, 1), date(2026, 12, 31)
            )
            self.assertEqual(
                [item["start_at"][:10] for item in calendar["items"]],
                ["2026-08-31", "2026-10-01", "2026-11-30"],
            )
            self.assertEqual(calendar["items"][1]["title"], "Moved dentist")
            self.assertEqual(calendar["items"][1]["occurrence_date"], "2026-09-30")
            self.assertEqual(calendar["items"][0]["series_id"], event_id)
            database.close()

    def test_recurrence_is_limited_to_events(self):
        with self.assertRaisesRegex(ValueError, "Only events can recur"):
            ItemDraft(kind="task", title="Take out trash", recurrence="weekly")
        with self.assertRaisesRegex(ValueError, "must start on a month's last day"):
            ItemDraft(
                kind="event",
                title="Month end",
                start_date="2026-02-27",
                recurrence="monthly",
                monthly_on_last_day=True,
            )

    def test_member_role_and_removal_keep_existing_items(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            member_id = database.add_member("test-family", "Lin", "Mom")
            database.create_items(
                "test-family", "submission", "note", "text", "UTC", member_id, None,
                [{"kind": "note", "title": "Keep me"}],
            )
            database.delete_member("test-family", member_id)
            board = database.get_board("test-family")
            self.assertEqual(board["members"], [])
            self.assertEqual(board["items"][0]["title"], "Keep me")
            database.close()

    def test_manual_edits_follow_each_item_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            actor_id = database.add_member("test-family", "Lin")
            event_id, task_id, note_id = database.create_items(
                "test-family",
                "submission",
                "three items",
                "text",
                "America/Toronto",
                actor_id,
                None,
                [
                    {
                        "kind": "event",
                        "title": "Pickup",
                        "start_date": "2026-08-01",
                        "all_day": True,
                        "recurrence": "daily",
                    },
                    {
                        "kind": "task",
                        "title": "Pay bill",
                        "due_date": "2026-08-02",
                    },
                    {"kind": "note", "title": "Door code"},
                ],
            )
            database.update_occurrence(
                "test-family",
                event_id,
                "2026-08-02",
                actor_id,
                {"title": "Late pickup"},
            )
            database.update_item(
                "test-family",
                event_id,
                actor_id,
                {"title": "School pickup", "start_date": "2026-08-03"},
            )
            database.update_item(
                "test-family",
                task_id,
                actor_id,
                {
                    "title": "Pay hydro bill",
                    "due_date": None,
                    "due_at": "2026-08-02T18:00:00-04:00",
                },
            )
            database.update_item(
                "test-family",
                note_id,
                actor_id,
                {"title": "Front door code", "details": "1234"},
            )

            items = {
                item["kind"]: item
                for item in database.get_board("test-family")["items"]
            }
            self.assertEqual(items["event"]["start_date"], "2026-08-03")
            self.assertEqual(items["task"]["due_at"], "2026-08-02T18:00:00-04:00")
            self.assertEqual(items["note"]["details"], "1234")
            self.assertEqual(
                database.connection.execute(
                    "SELECT COUNT(*) FROM recurrence_exceptions"
                ).fetchone()[0],
                0,
            )
            with self.assertRaisesRegex(ValueError, "Notes only"):
                database.update_item(
                    "test-family", note_id, actor_id, {"status": "done"}
                )
            database.close()

    def test_task_assignment_can_be_accepted_or_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            lin_id = database.add_member("test-family", "Lin")
            sam_id = database.add_member("test-family", "Sam")
            task_id = database.create_items(
                "test-family", "submission", "Two chores", "text", "UTC", lin_id,
                sam_id, [{"kind": "task", "title": "Wash dishes"}],
            )[0]
            task = database.get_board("test-family")["items"][0]
            self.assertEqual((task["owner_id"], task["assignment_state"], task["status"]), (sam_id, "pending", "unclaimed"))
            with self.assertRaisesRegex(ValueError, "must accept or reject"):
                database.update_item("test-family", task_id, sam_id, {"status": "claimed"})

            database.respond_to_task_assignment("test-family", task_id, sam_id, True)
            task = database.get_board("test-family")["items"][0]
            self.assertEqual((task["owner_id"], task["assignment_state"], task["status"]), (sam_id, "accepted", "claimed"))

            database.update_item("test-family", task_id, lin_id, {"owner_id": sam_id})
            database.respond_to_task_assignment("test-family", task_id, sam_id, False)
            task = database.get_board("test-family")["items"][0]
            self.assertEqual((task["owner_id"], task["assignment_state"], task["status"]), (None, None, "unclaimed"))
            database.close()


if __name__ == "__main__":
    unittest.main()
