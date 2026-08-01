import unittest
from copy import deepcopy
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from backend.hearthbook.domain.calendar import get_today
from backend.hearthbook.domain.models import CaptureAnalysis, ItemDraft, RouteDecision
from backend.hearthbook.llm.graph import conversation_text
from backend.hearthbook.llm.query import query_assistant
from backend.hearthbook.services.board import BoardService
from backend.hearthbook.storage.board import BoardDatabase


class EmptyExceptions:
    def table(self, _name):
        return self

    def select(self, _columns):
        return self

    def in_(self, _column, _values):
        return self

    def execute(self):
        return SimpleNamespace(data=[])


class MemoryDatabase:
    def __init__(self, items=None):
        self.members = [
            {"id": "lin", "name": "Lin", "role": "Parent"},
            {"id": "sam", "name": "Sam", "role": "Driver"},
        ]
        self.items = items or []
        self.memory = ""
        self.client = EmptyExceptions()

    def require_member(self, _household_id, member_id):
        if member_id not in {member["id"] for member in self.members}:
            raise ValueError("Choose a valid family member first")
        return member_id

    def get_board(self, _household_id):
        return {
            "household": {"id": "family", "timezone": "America/Toronto"},
            "members": deepcopy(self.members),
            "items": deepcopy(self.items),
        }

    def get_household_memory(self, _household_id):
        return self.memory

    def set_household_memory(self, _household_id, memory):
        self.memory = memory


def add_message(_database, _household_id, _session_id, _actor_id, role, content):
    SESSION["messages"].append({"role": role, "content": content})
    return deepcopy(SESSION)


def update_conversation(
    _database, _household_id, _session_id, _actor_id, *, status, intent, payload
):
    SESSION.update(status=status, intent=intent, payload=deepcopy(payload))
    return deepcopy(SESSION)


SESSION = {}


class BoardContractTest(unittest.IsolatedAsyncioTestCase):
    def test_voice_source_is_marked_only_in_prompt_context(self):
        session = {"messages": [{"role": "user", "content": "提醒我买牛奶"}]}

        self.assertIn("这是用户语音输入的", conversation_text(session, "audio"))
        self.assertNotIn("这是用户语音输入的", conversation_text(session))

    async def test_capture_routes_to_its_specialist_and_keeps_reminder_target(self):
        SESSION.clear()
        SESSION.update(
            id="session",
            actor_id="lin",
            timezone="America/Toronto",
            status="active",
            intent=None,
            payload={},
            messages=[{"role": "user", "content": "School pickup Saturday"}],
        )
        route = SimpleNamespace(
            ainvoke=AsyncMock(return_value=RouteDecision(intent="capture"))
        )
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
                            remind_member_id="sam",
                        )
                    ],
                )
            )
        )
        with (
            patch("backend.hearthbook.llm.graph.router_chain", return_value=route),
            patch("backend.hearthbook.llm.graph.capture_chain", return_value=capture),
            patch(
                "backend.hearthbook.services.board.create_conversation",
                return_value=deepcopy(SESSION),
            ) as create,
            patch("backend.hearthbook.llm.graph.add_message", side_effect=add_message),
            patch("backend.hearthbook.llm.graph.update_conversation", side_effect=update_conversation),
        ):
            response = await BoardService(MemoryDatabase(), "family", "lin").message(
                {
                    "text": "School pickup Saturday",
                    "actor_id": "sam",
                    "timezone": "America/Toronto",
                }
            )

        self.assertEqual(response["intent"], "capture")
        self.assertEqual(response["status"], "review")
        self.assertEqual(response["drafts"][0]["remind_member_id"], "sam")
        self.assertEqual(create.call_args.args[2], "lin")
        route.ainvoke.assert_awaited_once()

    def test_today_and_read_only_sql_projection(self):
        items = [
            {
                "id": "event", "kind": "event", "title": "Dentist", "details": "",
                "start_at": "2026-08-01T15:00:00-04:00", "end_at": None,
                "start_date": None, "due_at": None, "due_date": None,
                "reminder_at": "2026-08-01T14:00:00-04:00", "all_day": False,
                "recurrence": None, "recurrence_until": None,
                "monthly_on_last_day": False, "completed_at": None,
                "preparation": None, "remind_member_id": "sam", "notes": [],
                "created_at": "2026-07-31T00:00:00+00:00",
                "updated_at": "2026-07-31T00:00:00+00:00", "original_text": "Dentist",
            },
            {
                "id": "overdue", "kind": "task", "title": "Return book", "details": "",
                "start_at": None, "end_at": None, "start_date": None, "due_at": None,
                "due_date": "2026-07-31", "reminder_at": None, "all_day": False,
                "recurrence": None, "recurrence_until": None,
                "monthly_on_last_day": False, "completed_at": None,
                "preparation": None, "remind_member_id": None,
                "notes": [{"id": "n1", "member_id": "lin", "content": "Renewed", "created_at": "2026-07-31T01:00:00+00:00"}],
                "created_at": "2026-07-30T00:00:00+00:00",
                "updated_at": "2026-07-30T00:00:00+00:00", "original_text": "Return book",
            },
        ]
        database = MemoryDatabase(items)
        summary = get_today(database, "family", date(2026, 8, 1), "America/Toronto")
        reasons = {item["id"]: item["today_reasons"] for item in summary["items"]}
        self.assertEqual(set(reasons["event"]), {"happens_today", "reminder_today"})
        self.assertEqual(reasons["overdue"], ["overdue"])

        with patch("backend.hearthbook.llm.query.get_calendar", return_value={"items": []}):
            self.assertEqual(
                query_assistant(database, "family", "UTC", "SELECT title FROM items ORDER BY title"),
                [{"title": "Dentist"}, {"title": "Return book"}],
            )
            with self.assertRaisesRegex(ValueError, "read-only SELECT"):
                query_assistant(database, "family", "UTC", "DELETE FROM items")

    def test_recurrence_remains_event_only(self):
        with self.assertRaisesRegex(ValueError, "Only events can recur"):
            ItemDraft(kind="task", title="Trash", recurrence="weekly")

    def test_series_rule_and_single_occurrence_can_be_edited(self):
        client = MagicMock()
        items = MagicMock()
        exceptions = MagicMock()
        for table in (items, exceptions):
            for method in ("select", "eq", "limit", "update", "delete", "upsert"):
                getattr(table, method).return_value = table
        client.table.side_effect = lambda name: items if name == "items" else exceptions
        row = {
            "id": "series", "household_id": "family", "kind": "event",
            "title": "Pickup", "details": "", "preparation": None,
            "remind_member_id": None, "completed_at": None,
            "start_at": "2026-08-24T15:00:00-04:00",
            "end_at": "2026-08-24T16:00:00-04:00", "start_date": None,
            "due_at": None, "due_date": None, "reminder_at": None,
            "all_day": False, "recurrence": "weekly",
            "monthly_on_last_day": False, "recurrence_until": "2026-12-31",
        }
        items.execute.return_value = SimpleNamespace(data=[row])
        database = BoardDatabase(client)
        database.require_member = MagicMock(return_value="lin")
        database.get_household = MagicMock(return_value={"timezone": "America/Toronto"})

        database.update_item(
            "family", "series", "lin",
            {
                "start_at": "2026-08-31T15:00:00-04:00",
                "end_at": "2026-08-31T16:00:00-04:00",
                "recurrence": "monthly", "monthly_on_last_day": True,
            },
        )
        updated = items.update.call_args.args[0]
        self.assertEqual(updated["recurrence"], "monthly")
        self.assertTrue(updated["monthly_on_last_day"])
        exceptions.delete.assert_called_once()

        items.execute.return_value = SimpleNamespace(data=[{**row, **updated}])
        database.update_occurrence(
            "family", "series", "2026-09-30", "lin",
            {
                "title": "Late pickup", "details": "", "preparation": None,
                "start_at": "2026-10-01T17:00:00-04:00",
                "end_at": "2026-10-01T18:00:00-04:00", "start_date": None,
            },
        )
        exception = exceptions.upsert.call_args.args[0]
        self.assertEqual(exception["occurrence_date"], "2026-09-30")
        self.assertEqual(exception["start_at"], "2026-10-01T17:00:00-04:00")


if __name__ == "__main__":
    unittest.main()
