import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

from board_db import HOUSEHOLD_MEMORY_MAX_CHARS, BoardDatabase
from board_graph import (
    AssistantAction,
    AssistantQueryPlan,
    AssistantReply,
    BoardService,
    ExtractionResult,
    IntakeAnalysis,
    IntakeItemDraft,
    ItemDraft,
)


class BoardFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_assistant_is_scoped_keeps_conversation_and_proposes_updates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            lin_id = database.add_member("test-family", "Lin")
            other_id = database.add_member("other-family", "Other")
            database.create_items(
                "test-family",
                "family-item",
                "Pay bill",
                "text",
                "UTC",
                lin_id,
                None,
                [{"kind": "task", "title": "Pay hydro bill"}],
            )
            database.create_items(
                "other-family",
                "other-item",
                "Private note",
                "text",
                "UTC",
                other_id,
                None,
                [{"kind": "note", "title": "Other household secret"}],
            )
            database.set_household_memory(
                "test-family", "- Lin prefers concise English replies."
            )
            self.assertEqual(
                database.query_assistant(
                    "test-family", "UTC", "SELECT title FROM items"
                ),
                [{"title": "Pay hydro bill"}],
            )
            with self.assertRaisesRegex(ValueError, "read-only SELECT"):
                database.query_assistant(
                    "test-family", "UTC", "DELETE FROM items"
                )

            service = BoardService(database, "test-family")
            plans = [
                AssistantQueryPlan(sql="SELECT title FROM items"),
                AssistantQueryPlan(
                    sql="SELECT title FROM items WHERE title LIKE '%bill%'"
                ),
            ]
            replies = [
                AssistantReply(message="You have one task."),
                AssistantReply(
                    message="It is the hydro bill.",
                    action=AssistantAction(
                        item_id=database.get_board("test-family")["items"][0]["id"],
                        fields={"status": "done"},
                        confirmation="Mark Pay hydro bill as done?",
                    ),
                    updated_memory="- Lin prefers concise bilingual replies.",
                ),
            ]
            with (
                patch(
                    "board_graph.plan_assistant_query",
                    AsyncMock(side_effect=plans),
                ) as planner,
                patch(
                    "board_graph.answer_assistant_with_openrouter",
                    AsyncMock(side_effect=replies),
                ) as answer,
            ):
                first = await service.assistant(
                    {
                        "text": "What tasks do I have?",
                        "actor_id": lin_id,
                        "timezone": "UTC",
                    }
                )
                second = await service.assistant(
                    {
                        "text": "Which bill?",
                        "actor_id": lin_id,
                        "session_id": first["session_id"],
                    }
                )
                self.assertEqual(second["session_id"], first["session_id"])
                self.assertEqual(len(second["messages"]), 4)
                self.assertEqual(second["action"]["fields"], {"status": "done"})
                self.assertEqual(
                    database.get_board("test-family")["items"][0]["status"],
                    "unclaimed",
                )
                database.update_item(
                    "test-family",
                    second["action"]["item_id"],
                    lin_id,
                    second["action"]["fields"],
                )
                self.assertEqual(
                    database.get_board("test-family")["items"][0]["status"],
                    "done",
                )
                self.assertIn(
                    "assistant: You have one task.",
                    planner.await_args.args[0],
                )
                self.assertIn(
                    "Pay hydro bill",
                    answer.await_args.kwargs["query_results"],
                )
                self.assertIn("concise English", planner.await_args.args[4])
                self.assertIn(
                    "concise English", answer.await_args.kwargs["memory"]
                )
                self.assertEqual(
                    database.get_household_memory("test-family"),
                    "- Lin prefers concise bilingual replies.",
                )
                with self.assertRaisesRegex(ValueError, "Unsupported"):
                    AssistantAction(
                        item_id="item",
                        fields={"delete": True},
                        confirmation="Delete it?",
                    )
            database.close()

    async def test_household_memory_is_scoped_and_capped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            database.set_household_memory(
                "family-a", "x" * (HOUSEHOLD_MEMORY_MAX_CHARS + 100)
            )
            database.set_household_memory("family-b", "separate")

            self.assertEqual(
                len(database.get_household_memory("family-a")),
                HOUSEHOLD_MEMORY_MAX_CHARS,
            )
            self.assertEqual(
                database.get_household_memory("family-b"), "separate"
            )
            self.assertEqual(database.get_household_memory("family-c"), "")
            database.close()

    async def test_intake_confirmation_keeps_owner_and_preparation_editable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            lin_id = database.add_member("test-family", "Lin", "Parent")
            sam_id = database.add_member("test-family", "Sam", "Driver")
            database.create_items(
                "test-family",
                "existing",
                "Dentist",
                "text",
                "America/Toronto",
                lin_id,
                None,
                [
                    {
                        "kind": "event",
                        "title": "Dentist",
                        "start_at": "2026-08-01T15:00:00-04:00",
                        "end_at": "2026-08-01T16:00:00-04:00",
                        "reminder_at": "2026-08-01T14:30:00-04:00",
                    }
                ],
            )
            service = BoardService(database, "test-family")
            database.set_household_memory(
                "test-family", "- Sam usually handles school pickup."
            )
            responses = [
                IntakeAnalysis(
                    status="clarify",
                    message="What time should pickup start?",
                    updated_memory=(
                        "- Sam usually handles school pickup.\n"
                        "- The family prefers Chinese."
                    ),
                ),
                IntakeAnalysis(
                    status="review",
                    message="Please review this event.",
                    updated_memory="- Sam handles school pickup on Fridays.",
                    items=[
                        IntakeItemDraft(
                            kind="event",
                            title="School pickup",
                            start_at="2026-08-01T15:30:00-04:00",
                            end_at="2026-08-01T16:30:00-04:00",
                            reminder_at="2026-08-01T15:00:00-04:00",
                            owner_id=sam_id,
                            preparation="Bring the pickup card.",
                        ),
                        IntakeItemDraft(
                            kind="task",
                            title="Return school form",
                            owner_id=lin_id,
                            preparation="Find the form in the backpack.",
                        ),
                    ],
                ),
            ]
            with patch(
                "board_graph.analyze_intake_with_openrouter",
                AsyncMock(side_effect=responses),
            ) as analyze:
                intake = await service.intake(
                    {
                        "text": "School pickup Friday",
                        "actor_id": lin_id,
                        "timezone": "America/Toronto",
                        "source": "text",
                    }
                )
                self.assertEqual(intake["status"], "clarifying")
                self.assertEqual(len(database.get_board("test-family")["items"]), 1)

                intake = await service.intake(
                    {
                        "text": "3:30 PM",
                        "actor_id": lin_id,
                        "session_id": intake["session_id"],
                    }
                )
                self.assertEqual(intake["status"], "review")
                self.assertEqual(intake["drafts"][0]["owner_id"], sam_id)
                self.assertEqual(intake["conflicts"][0]["kind"], "time")
                self.assertIn("role=Driver", analyze.await_args.kwargs["family"])
                self.assertIn(
                    "family prefers Chinese", analyze.await_args.kwargs["memory"]
                )
                self.assertEqual(
                    database.get_household_memory("test-family"),
                    "- Sam handles school pickup on Fridays.",
                )
                self.assertEqual(len(database.get_board("test-family")["items"]), 1)

                board = await service.confirm_intake(
                    intake["session_id"],
                    lin_id,
                    [lin_id, sam_id],
                    [True, False],
                )
                created = next(
                    item for item in board["items"] if item["title"] == "School pickup"
                )
                self.assertEqual(created["owner_id"], lin_id)
                self.assertEqual(created["preparation"], "Bring the pickup card.")
                rejected = next(
                    item for item in board["items"] if item["title"] == "Return school form"
                )
                self.assertEqual(rejected["owner_id"], sam_id)
                self.assertIsNone(rejected["preparation"])
                self.assertEqual(len(board["items"]), 3)
            database.close()

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
                        reminder_at="2026-08-31T14:30:00-04:00",
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
            database.update_item(
                "test-family",
                event_id,
                actor_id,
                {"preparation": "Bring insurance card"},
            )
            await service.execute(
                {
                    "type": "update_occurrence",
                    "item_id": event_id,
                    "occurrence_date": "2026-09-30",
                    "actor_id": actor_id,
                    "fields": {
                        "title": "Moved dentist",
                        "preparation": "Bring new insurance card",
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
            self.assertEqual(
                calendar["items"][1]["preparation"], "Bring new insurance card"
            )
            self.assertEqual(
                calendar["items"][2]["preparation"], "Bring insurance card"
            )
            self.assertEqual(calendar["items"][1]["occurrence_date"], "2026-09-30")
            self.assertEqual(calendar["items"][2]["reminder_at"], "2026-11-30T14:30:00-05:00")
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

    def test_reminder_persists_for_events_and_tasks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = BoardDatabase(Path(temp_dir) / "test.sqlite3")
            database.setup()
            actor_id = database.add_member("test-family", "Lin")
            event_id, task_id = database.create_items(
                "test-family", "submission", "reminders", "text", "America/Toronto", actor_id, None,
                [
                    {"kind": "event", "title": "Dentist", "start_at": "2026-08-01T15:00:00-04:00", "reminder_at": "2026-08-01T14:30:00-04:00"},
                    {"kind": "task", "title": "Pay bill", "due_date": "2026-08-02", "reminder_at": "2026-08-02T09:00:00-04:00"},
                ],
            )
            database.update_item("test-family", event_id, actor_id, {"reminder_at": "2026-08-01T14:00:00-04:00"})
            reminders = {item["id"]: item["reminder_at"] for item in database.get_board("test-family")["items"]}
            self.assertEqual(reminders[event_id], "2026-08-01T14:00:00-04:00")
            self.assertEqual(reminders[task_id], "2026-08-02T09:00:00-04:00")
            database.close()

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
                    "preparation": "Find the account number",
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
            self.assertEqual(items["task"]["preparation"], "Find the account number")
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
