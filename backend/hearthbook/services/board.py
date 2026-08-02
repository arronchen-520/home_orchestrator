from __future__ import annotations

from datetime import date

from ..domain.calendar import get_calendar, get_today
from ..llm.graph import build_conversation_graph
from ..storage.board import BoardDatabase
from ..storage.conversation import add_message, confirm_conversation, create_conversation


class BoardService:
    def __init__(self, database: BoardDatabase, household_id: str, member_id: str):
        self.database = database
        self.household_id = household_id
        self.member_id = member_id
        self.graph = build_conversation_graph(database, household_id)

    def get_board(self, result: dict | None = None) -> dict:
        return {
            **self.database.get_board(self.household_id),
            "current_member_id": self.member_id,
            "result": result,
        }

    def get_calendar(self, start: date, end: date, timezone_name: str) -> dict:
        return get_calendar(self.database, self.household_id, start, end, timezone_name)

    def get_today(self, target: date, timezone_name: str) -> dict:
        return get_today(self.database, self.household_id, target, timezone_name)

    async def message(self, command: dict) -> dict:
        text = command.get("text", "").strip()
        if not text:
            raise ValueError("Message cannot be empty")
        session = (
            add_message(
                self.database, self.household_id, command["session_id"], self.member_id, "user", text
            )
            if command.get("session_id")
            else create_conversation(
                self.database, self.household_id, self.member_id, command.get("timezone", "UTC"), text
            )
        )
        state = await self.graph.ainvoke({"command": command, "session": session})
        return state["response"]

    def confirm_capture(
        self,
        session_id: str,
        remind_member_ids: list[list[str]],
        accepted_preparations: list[bool],
    ) -> dict:
        result = confirm_conversation(
            self.database,
            self.household_id,
            session_id,
            self.member_id,
            remind_member_ids,
            accepted_preparations,
        )
        return self.get_board(result)

    def update_item(self, item_id: str, fields: dict) -> dict:
        self.database.update_item(self.household_id, item_id, self.member_id, fields)
        return self.get_board({"action": "updated", "item_id": item_id})

    def update_member_profile(self, name: str, role: str) -> dict:
        self.database.update_member_profile(self.household_id, self.member_id, name, role)
        return self.get_board({"action": "member_profile_updated"})

    def add_item_note(self, item_id: str, content: str) -> dict:
        note_id = self.database.add_item_note(self.household_id, item_id, self.member_id, content)
        return self.get_board({"action": "note_added", "note_id": note_id})

    def update_occurrence(
        self, item_id: str, occurrence_date: str, fields: dict
    ) -> dict:
        self.database.update_occurrence(
            self.household_id, item_id, occurrence_date, self.member_id, fields
        )
        return self.get_board({"action": "occurrence_updated"})

    def cancel_occurrence(
        self, item_id: str, occurrence_date: str
    ) -> dict:
        self.database.cancel_occurrence(
            self.household_id, item_id, occurrence_date, self.member_id
        )
        return self.get_board({"action": "occurrence_cancelled"})

    def delete_item(self, item_id: str) -> dict:
        self.database.delete_item(self.household_id, item_id, self.member_id)
        return self.get_board({"action": "deleted"})
