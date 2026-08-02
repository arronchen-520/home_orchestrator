import unittest
from copy import deepcopy
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from backend.hearthbook.domain.calendar import get_today
from backend.hearthbook.domain.models import AgentReply, CaptureAnalysis, ItemDraft, RouteDecision
from backend.hearthbook.domain.recurrence import base_occurrences
from backend.hearthbook.llm.graph import conversation_text, query_context
from backend.hearthbook.services.board import BoardService
from backend.hearthbook.storage.board import BoardDatabase
from backend.hearthbook.storage.conversation import confirm_conversation


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
    def test_capture_review_falls_back_to_a_confirmation_message(self):
        review = CaptureAnalysis(
            status="review", message="", items=[ItemDraft(kind="note", title="Shopping list")]
        )

        self.assertEqual(review.message, "Please confirm the following.")
        with self.assertRaises(ValueError):
            CaptureAnalysis(status="clarify", message="")

    def test_voice_source_is_marked_only_in_prompt_context(self):
        session = {"messages": [{"role": "user", "content": "提醒我买牛奶"}]}

        self.assertIn("这是用户语音输入的", conversation_text(session, "audio"))
        self.assertNotIn("这是用户语音输入的", conversation_text(session))

    def test_image_source_is_marked_only_in_prompt_context(self):
        session = {"messages": [{"role": "user", "content": "Screenshot content: school event"}]}

        self.assertIn("这是用户图片输入的", conversation_text(session, "image"))
        self.assertNotIn("这是用户图片输入的", conversation_text(session))

    def test_single_message_context_excludes_prior_history(self):
        session = {
            "messages": [
                {"role": "user", "content": "Earlier request"},
                {"role": "assistant", "content": "Earlier reply"},
                {"role": "user", "content": "Latest request"},
            ]
        }

        self.assertEqual(conversation_text(session, limit=1), "user: Latest request")

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

    async def test_task_reminder_defaults_to_proposer(self):
        SESSION.clear()
        SESSION.update(
            id="session",
            actor_id="lin",
            timezone="America/Toronto",
            status="active",
            intent=None,
            payload={},
            messages=[{"role": "user", "content": "Buy milk tomorrow"}],
        )
        route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="capture")))
        capture = SimpleNamespace(
            ainvoke=AsyncMock(
                return_value=CaptureAnalysis(
                    status="review",
                    message="Please check this.",
                    items=[
                        ItemDraft(
                            kind="task",
                            title="Buy milk",
                            due_date="2026-08-02",
                            reminder_at="2026-08-02T09:00:00-04:00",
                        )
                    ],
                )
            )
        )
        with (
            patch("backend.hearthbook.llm.graph.router_chain", return_value=route),
            patch("backend.hearthbook.llm.graph.capture_chain", return_value=capture),
            patch("backend.hearthbook.services.board.create_conversation", return_value=deepcopy(SESSION)),
            patch("backend.hearthbook.llm.graph.add_message", side_effect=add_message),
            patch("backend.hearthbook.llm.graph.update_conversation", side_effect=update_conversation),
        ):
            response = await BoardService(MemoryDatabase(), "family", "lin").message(
                {"text": "Buy milk tomorrow", "timezone": "America/Toronto"}
            )

        self.assertEqual(response["drafts"][0]["remind_member_id"], "lin")

    async def test_event_reminder_defaults_to_proposer(self):
        SESSION.clear()
        SESSION.update(
            id="session",
            actor_id="lin",
            timezone="America/Toronto",
            status="active",
            intent=None,
            payload={},
            messages=[{"role": "user", "content": "My flight tomorrow"}],
        )
        route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="capture")))
        capture = SimpleNamespace(
            ainvoke=AsyncMock(
                return_value=CaptureAnalysis(
                    status="review",
                    message="Please check this.",
                    items=[
                        ItemDraft(
                            kind="event",
                            title="Flight",
                            start_at="2026-08-02T09:00:00-04:00",
                            reminder_at="2026-08-02T07:00:00-04:00",
                        )
                    ],
                )
            )
        )
        with (
            patch("backend.hearthbook.llm.graph.router_chain", return_value=route),
            patch("backend.hearthbook.llm.graph.capture_chain", return_value=capture),
            patch("backend.hearthbook.services.board.create_conversation", return_value=deepcopy(SESSION)),
            patch("backend.hearthbook.llm.graph.add_message", side_effect=add_message),
            patch("backend.hearthbook.llm.graph.update_conversation", side_effect=update_conversation),
        ):
            response = await BoardService(MemoryDatabase(), "family", "lin").message(
                {"text": "My flight tomorrow", "timezone": "America/Toronto"}
            )

        self.assertEqual(response["drafts"][0]["remind_member_id"], "lin")

    async def test_capture_separates_scheduled_event_from_action_task(self):
        SESSION.clear()
        SESSION.update(
            id="session",
            actor_id="lin",
            timezone="America/Toronto",
            status="active",
            intent=None,
            payload={},
            messages=[{"role": "user", "content": "周六下午要去看牙医，明天去买牛奶"}],
        )
        route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="capture")))
        capture = SimpleNamespace(
            ainvoke=AsyncMock(
                return_value=CaptureAnalysis(
                    status="review",
                    message="请确认这两项内容。",
                    items=[
                        ItemDraft(
                            kind="event",
                            title="看牙医",
                            start_at="2026-08-01T15:00:00-04:00",
                        ),
                        ItemDraft(
                            kind="task",
                            title="买牛奶",
                            due_date="2026-08-02",
                        ),
                    ],
                )
            )
        )
        with (
            patch("backend.hearthbook.llm.graph.router_chain", return_value=route),
            patch("backend.hearthbook.llm.graph.capture_chain", return_value=capture),
            patch("backend.hearthbook.services.board.create_conversation", return_value=deepcopy(SESSION)),
            patch("backend.hearthbook.llm.graph.add_message", side_effect=add_message),
            patch("backend.hearthbook.llm.graph.update_conversation", side_effect=update_conversation),
        ):
            response = await BoardService(MemoryDatabase(), "family", "lin").message(
                {"text": "周六下午要去看牙医，明天去买牛奶", "timezone": "America/Toronto"}
            )

        self.assertEqual([draft["kind"] for draft in response["drafts"]], ["event", "task"])
        self.assertEqual(response["drafts"][0]["start_at"], "2026-08-01T15:00:00-04:00")
        self.assertEqual(response["drafts"][1]["due_date"], "2026-08-02")

    def test_today(self):
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

    def test_query_context_keeps_recurring_series_compact(self):
        item = ItemDraft(
            kind="event", title="Workout", start_date="2026-08-03", all_day=True,
            recurrence="weekly", weekdays=["MO"], details="Bring shoes",
        ).model_dump(mode="json")
        item.update(id="workout", completed_at=None, notes=[])

        context = query_context(
            MemoryDatabase([item]), "family", "lin", "America/Toronto", date(2026, 8, 2)
        )

        self.assertEqual(context["current_member"]["id"], "lin")
        self.assertEqual(len(context["records"]), 1)
        self.assertEqual(context["records"][0]["repeat"], "every week on Monday")
        self.assertEqual(context["records"][0]["next_occurrence"]["occurrence_date"], "2026-08-03")

    async def test_query_receives_board_records_and_filters_unknown_references(self):
        SESSION.clear()
        SESSION.update(
            id="session", actor_id="lin", timezone="America/Toronto", status="active",
            intent=None, payload={}, messages=[{"role": "user", "content": "When is my flight?"}],
        )
        flight = ItemDraft(
            kind="event", title="Flight to Shanghai", start_at="2026-08-03T09:00:00-04:00",
            reminder_at="2026-08-03T07:00:00-04:00", remind_member_id="lin",
        ).model_dump(mode="json")
        flight.update(id="flight", completed_at=None, notes=[])
        route = SimpleNamespace(ainvoke=AsyncMock(return_value=RouteDecision(intent="query")))
        query = SimpleNamespace(
            ainvoke=AsyncMock(return_value=AgentReply(message="Your flight is at 9.", references=["flight", "missing"]))
        )
        with (
            patch("backend.hearthbook.llm.graph.router_chain", return_value=route),
            patch("backend.hearthbook.llm.graph.query_answer_chain", return_value=query),
            patch("backend.hearthbook.services.board.create_conversation", return_value=deepcopy(SESSION)),
            patch("backend.hearthbook.llm.graph.add_message", side_effect=add_message),
            patch("backend.hearthbook.llm.graph.update_conversation", side_effect=update_conversation),
        ):
            response = await BoardService(MemoryDatabase([flight]), "family", "lin").message(
                {"text": "When is my flight?", "timezone": "America/Toronto"}
            )

        self.assertEqual(response["references"], ["flight"])
        self.assertIn("Flight to Shanghai", query.ainvoke.call_args.args[0]["board"])
        self.assertIn('"id": "lin"', query.ainvoke.call_args.args[0]["current_member"])

    def test_recurrence_remains_event_only(self):
        with self.assertRaisesRegex(ValueError, "Only events can recur"):
            ItemDraft(kind="task", title="Trash", recurrence="weekly")

    def test_confirm_clears_session_messages_after_creating_items(self):
        database = MagicMock()
        session_table = MagicMock()
        message_table = MagicMock()
        database.client.table.side_effect = lambda name: {
            "conversation_sessions": session_table,
            "conversation_messages": message_table,
        }[name]
        message_table.delete.return_value = message_table
        database.create_items.return_value = ["item-1"]
        session = {
            "id": "session",
            "status": "review",
            "intent": "capture",
            "timezone": "UTC",
            "payload": {"drafts": [{"kind": "note", "title": "Buy milk"}]},
            "messages": [{"role": "user", "content": "Buy milk"}],
        }
        with patch("backend.hearthbook.storage.conversation.get_conversation", return_value=session):
            result = confirm_conversation(database, "family", "session", "lin", [None], [False])

        self.assertEqual(result["item_ids"], ["item-1"])
        message_table.delete.assert_called_once_with()
        message_table.eq.assert_called_once_with("session_id", "session")

    def test_today_finds_a_recurring_reminder_after_its_occurrence(self):
        item = ItemDraft(
            kind="event", title="Medicine", start_date="2026-08-03", all_day=True,
            recurrence="weekly", reminder_at="2026-08-04T09:00:00-04:00",
            remind_member_id="sam",
        ).model_dump(mode="json")
        item.update(id="medicine", completed_at=None, notes=[])

        result = get_today(
            MemoryDatabase([item]), "family", date(2026, 8, 4), "America/Toronto"
        )

        self.assertEqual(result["items"][0]["today_reasons"], ["reminder_today"])

    def test_weekly_recurrence_supports_any_weekday_combination(self):
        item = ItemDraft(
            kind="event", title="Workout", start_date="2026-08-03",
            recurrence="weekly", weekdays=["FR", "MO", "WE", "MO"],
        ).model_dump(mode="json")

        self.assertEqual(item["weekdays"], ["MO", "WE", "FR"])
        self.assertEqual(
            [value.date() for value in base_occurrences(
                item, date(2026, 8, 1), date(2026, 8, 9), "America/Toronto"
            )],
            [date(2026, 8, 3), date(2026, 8, 5), date(2026, 8, 7)],
        )

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
