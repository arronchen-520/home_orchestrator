from __future__ import annotations

import asyncio
import os
from calendar import monthrange
from datetime import date, datetime
from functools import lru_cache
from typing import Literal, TypedDict
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, model_validator

from board_db import BoardDatabase

ItemKind = Literal["event", "task", "note"]
Recurrence = Literal["daily", "weekly", "monthly"]


class ConfigurationError(RuntimeError):
    pass


class ItemDraft(BaseModel):
    kind: ItemKind = Field(
        description=(
            "event for an occurrence; task for an action or chore; "
            "note for reference information"
        )
    )
    title: str = Field(min_length=1, max_length=120)
    details: str = Field(default="", max_length=2000)
    start_at: datetime | None = Field(
        default=None, description="Timed event start; ISO 8601 with timezone"
    )
    end_at: datetime | None = Field(
        default=None, description="Optional timed event end; ISO 8601 with timezone"
    )
    start_date: date | None = Field(
        default=None, description="All-day event date; YYYY-MM-DD"
    )
    due_at: datetime | None = Field(
        default=None, description="Task deadline with a stated time and timezone"
    )
    due_date: date | None = Field(
        default=None, description="Task deadline when only a date is stated"
    )
    all_day: bool = False
    recurrence: Recurrence | None = Field(
        default=None,
        description="Event repetition: daily, weekly, monthly, or null",
    )
    monthly_on_last_day: bool = False
    recurrence_until: date | None = Field(
        default=None, description="Inclusive final recurrence date; YYYY-MM-DD"
    )

    @model_validator(mode="after")
    def match_kind(self) -> ItemDraft:
        for value in (self.start_at, self.end_at, self.due_at):
            if value is not None and value.utcoffset() is None:
                raise ValueError("Date-times require a timezone")

        if self.kind == "event":
            first = self.start_date or (self.start_at.date() if self.start_at else None)
            if self.recurrence_until is not None:
                if self.recurrence is None:
                    raise ValueError("A recurrence end date requires recurrence")
                if first and self.recurrence_until < first:
                    raise ValueError("Recurrence end date cannot precede its start")
            if self.monthly_on_last_day:
                if self.recurrence != "monthly":
                    raise ValueError("Last-day recurrence must be monthly")
                if first and first.day != monthrange(first.year, first.month)[1]:
                    raise ValueError("Last-day recurrence must start on a month's last day")
            self.due_at = self.due_date = None
            if self.start_date is not None:
                self.all_day = True
            if self.all_day:
                if self.start_date is None and self.start_at is not None:
                    self.start_date = self.start_at.date()
                if self.start_date is None:
                    raise ValueError("An all-day event requires start_date")
                self.start_at = self.end_at = None
            else:
                if self.start_at is None:
                    raise ValueError("A timed event requires start_at")
                self.start_date = None
                if self.end_at is not None and self.end_at < self.start_at:
                    raise ValueError("Event end must be after its start")
        elif self.kind == "task":
            if (
                self.recurrence is not None
                or self.monthly_on_last_day
                or self.recurrence_until is not None
            ):
                raise ValueError("Only events can recur")
            self.start_at = self.end_at = self.start_date = None
            self.all_day = False
            if self.due_at is not None and self.due_date is not None:
                raise ValueError("A task cannot have both due_at and due_date")
        else:
            if (
                self.recurrence is not None
                or self.monthly_on_last_day
                or self.recurrence_until is not None
            ):
                raise ValueError("Only events can recur")
            self.start_at = self.end_at = self.start_date = None
            self.due_at = self.due_date = None
            self.all_day = False
        return self


class ExtractionResult(BaseModel):
    items: list[ItemDraft] = Field(min_length=1, max_length=20)


class IngestionState(TypedDict, total=False):
    command: dict
    drafts: list[dict]
    result: dict


@lru_cache(maxsize=1)
def openrouter_chain():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENROUTER_API_KEY is not configured")

    parser = PydanticOutputParser(pydantic_object=ExtractionResult)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You turn short household board input in Chinese or English into one or more items.

Rules:
- Split independent events, tasks, and notes into separate items.
- Preserve the input language in each title and details.
- event: an appointment, gathering, or occurrence.
- task: an action, chore, request, or shopping item.
- note: reference information with no action to perform.
- Resolve relative dates using the supplied current time and IANA timezone.
- Use start_date/due_date for date-only input and set all_day for date-only events.
- Use start_at/due_at only when a time is stated.
- For an event repeated every day, week, or month, set recurrence to daily, weekly, or monthly.
- For "the last day of every month", also set monthly_on_last_day to true and
  resolve the first occurrence to the current or next month-end.
- "Every month on the 31st" is not a last-day rule; leave monthly_on_last_day false.
- If the input states when repetition ends, set recurrence_until to that inclusive date.
- Treat recurring scheduled actions as events; recurrence is not supported for tasks or notes.
- A recurring event still needs its first stated date or date-time.
- Never invent a date, time, owner, or assignee.
- Keep each title concise and put remaining useful text in details.

{format_instructions}""",
            ),
            (
                "human",
                "Current time: {now}\nTimezone: {timezone_name}\nInput: {text}",
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    model = ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        temperature=0,
        default_headers={"X-OpenRouter-Title": "Home Orchestrator"},
    )
    return prompt | model | parser


async def parse_with_openrouter(
    text: str, now: str, timezone_name: str
) -> ExtractionResult:
    return await openrouter_chain().ainvoke(
        {"text": text, "now": now, "timezone_name": timezone_name}
    )


def build_ingestion_graph(database: BoardDatabase):
    async def extract_items(state: IngestionState) -> dict:
        command = state["command"]
        timezone_name = command.get("timezone", "UTC")
        try:
            local_now = datetime.now(ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Invalid timezone") from exc
        extraction = await parse_with_openrouter(
            command["text"], local_now.isoformat(), timezone_name
        )
        return {
            "drafts": [
                item.model_dump(mode="json") for item in extraction.items
            ]
        }

    def save_items(state: IngestionState) -> dict:
        command = state["command"]
        drafts = [
            ItemDraft.model_validate(draft).model_dump(mode="json")
            for draft in state["drafts"]
        ]
        item_ids = database.create_items(
            household_id=command["household_id"],
            submission_id=command["submission_id"],
            text=command["text"],
            source=command.get("source", "text"),
            timezone_name=command.get("timezone", "UTC"),
            actor_id=command["actor_id"],
            owner_id=command.get("owner_id"),
            drafts=drafts,
        )
        return {
            "drafts": [],
            "result": {
                "action": "created",
                "item_id": item_ids[0],
                "item_ids": item_ids,
            },
        }

    builder = StateGraph(IngestionState)
    builder.add_node("extract_items", extract_items)
    builder.add_node("save_items", save_items)
    builder.add_edge(START, "extract_items")
    builder.add_edge("extract_items", "save_items")
    builder.add_edge("save_items", END)
    return builder.compile()


class BoardService:
    def __init__(
        self,
        database: BoardDatabase,
        household_id: str = "family-default",
    ):
        self.database = database
        self.household_id = household_id
        self.graph = build_ingestion_graph(database)
        # ponytail: one-process lock; SQLite transactions become the write boundary.
        self._lock = asyncio.Lock()

    async def get_board(self, result: dict | None = None) -> dict:
        return {**self.database.get_board(self.household_id), "result": result}

    async def get_calendar(self, start_date: date, end_date: date) -> dict:
        return self.database.get_calendar(self.household_id, start_date, end_date)

    def get_weather_location(self) -> dict | None:
        return self.database.get_weather_location(self.household_id)

    async def set_household_location(self, location: dict) -> dict:
        async with self._lock:
            self.database.set_household_location(self.household_id, location)
            return await self.get_board({"action": "household_updated"})

    async def execute(self, command: dict) -> dict:
        async with self._lock:
            command_type = command.get("type")
            if command_type == "add_item":
                self.database.require_member(
                    self.household_id, command.get("actor_id")
                )
                if command.get("owner_id") is not None:
                    self.database.require_member(
                        self.household_id, command["owner_id"]
                    )
                submission_id = str(uuid4())
                graph_command = {
                    **command,
                    "household_id": self.household_id,
                    "submission_id": submission_id,
                }
                state = await self.graph.ainvoke(
                    {"command": graph_command},
                    {"configurable": {"thread_id": submission_id}},
                )
                return await self.get_board(state["result"])
            if command_type == "add_member":
                member_id = self.database.add_member(
                    self.household_id, command.get("name", ""), command.get("role", "")
                )
                return await self.get_board(
                    {"action": "member_added", "member_id": member_id}
                )
            if command_type == "delete_member":
                self.database.delete_member(self.household_id, command["member_id"])
                return await self.get_board({"action": "member_deleted"})
            if command_type == "update_item":
                self.database.update_item(
                    self.household_id,
                    command["item_id"],
                    command.get("actor_id"),
                    command.get("fields", {}),
                )
                return await self.get_board(
                    {"action": "updated", "item_id": command["item_id"]}
                )
            if command_type == "respond_to_task_assignment":
                self.database.respond_to_task_assignment(
                    self.household_id,
                    command["item_id"],
                    command.get("actor_id"),
                    command["accept"],
                )
                return await self.get_board(
                    {
                        "action": "assignment_accepted"
                        if command["accept"] else "assignment_rejected",
                        "item_id": command["item_id"],
                    }
                )
            if command_type == "update_occurrence":
                self.database.update_occurrence(
                    self.household_id,
                    command["item_id"],
                    command["occurrence_date"],
                    command.get("actor_id"),
                    command.get("fields", {}),
                )
                return await self.get_board(
                    {
                        "action": "occurrence_updated",
                        "item_id": command["item_id"],
                        "occurrence_date": command["occurrence_date"],
                    }
                )
            if command_type == "cancel_occurrence":
                self.database.cancel_occurrence(
                    self.household_id,
                    command["item_id"],
                    command["occurrence_date"],
                    command.get("actor_id"),
                )
                return await self.get_board(
                    {
                        "action": "occurrence_cancelled",
                        "item_id": command["item_id"],
                        "occurrence_date": command["occurrence_date"],
                    }
                )
            if command_type == "delete_item":
                self.database.delete_item(
                    self.household_id,
                    command["item_id"],
                    command.get("actor_id"),
                )
                return await self.get_board(
                    {"action": "deleted", "item_id": command["item_id"]}
                )
            raise ValueError("Unsupported command")
