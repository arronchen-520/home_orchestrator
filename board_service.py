from __future__ import annotations

from datetime import date

from board_calendar import get_calendar, get_today
from board_db import BoardDatabase
from board_graph import build_conversation_graph
from conversation_db import add_message, confirm_conversation, create_conversation


class BoardService:
    def __init__(self, database: BoardDatabase, household_id: str):
        self.database = database
        self.household_id = household_id
        self.graph = build_conversation_graph(database, household_id)

    def get_board(self, result: dict | None = None) -> dict:
        return {**self.database.get_board(self.household_id), "result": result}

    def get_calendar(self, start: date, end: date) -> dict:
        return get_calendar(self.database, self.household_id, start, end)

    def get_today(self, target: date, timezone_name: str) -> dict:
        return get_today(self.database, self.household_id, target, timezone_name)

    async def message(self, command: dict) -> dict:
        actor_id = self.database.require_member(self.household_id, command.get("actor_id"))
        text = command.get("text", "").strip()
        if not text:
            raise ValueError("Message cannot be empty")
        session = (
            add_message(
                self.database, self.household_id, command["session_id"], actor_id, "user", text
            )
            if command.get("session_id")
            else create_conversation(
                self.database, self.household_id, actor_id, command.get("timezone", "UTC"), text
            )
        )
        state = await self.graph.ainvoke({"command": command, "session": session})
        return state["response"]

    def confirm_capture(
        self,
        session_id: str,
        actor_id: str,
        remind_member_ids: list[str | None],
        accepted_preparations: list[bool],
    ) -> dict:
        result = confirm_conversation(
            self.database,
            self.household_id,
            session_id,
            actor_id,
            remind_member_ids,
            accepted_preparations,
        )
        return self.get_board(result)

    def update_item(self, item_id: str, actor_id: str, fields: dict) -> dict:
        self.database.update_item(self.household_id, item_id, actor_id, fields)
        return self.get_board({"action": "updated", "item_id": item_id})

    def add_item_note(self, item_id: str, actor_id: str, content: str) -> dict:
        note_id = self.database.add_item_note(self.household_id, item_id, actor_id, content)
        return self.get_board({"action": "note_added", "note_id": note_id})

    def update_occurrence(
        self, item_id: str, occurrence_date: str, actor_id: str, fields: dict
    ) -> dict:
        self.database.update_occurrence(
            self.household_id, item_id, occurrence_date, actor_id, fields
        )
        return self.get_board({"action": "occurrence_updated"})

    def cancel_occurrence(
        self, item_id: str, occurrence_date: str, actor_id: str
    ) -> dict:
        self.database.cancel_occurrence(
            self.household_id, item_id, occurrence_date, actor_id
        )
        return self.get_board({"action": "occurrence_cancelled"})

    def delete_item(self, item_id: str, actor_id: str) -> dict:
        self.database.delete_item(self.household_id, item_id, actor_id)
        return self.get_board({"action": "deleted"})
