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
    reminder_at: datetime | None = Field(
        default=None, description="One reminder time; ISO 8601 with timezone"
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
        for value in (self.start_at, self.end_at, self.due_at, self.reminder_at):
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
            if self.reminder_at is not None:
                if self.all_day:
                    if self.reminder_at.date() > self.start_date:
                        raise ValueError("Reminder must not follow the event date")
                elif self.reminder_at >= self.start_at:
                    raise ValueError("Reminder must precede the event")
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
            if self.reminder_at is not None:
                if self.due_at is not None and self.reminder_at >= self.due_at:
                    raise ValueError("Reminder must precede the task deadline")
                if self.due_date is not None and self.reminder_at.date() > self.due_date:
                    raise ValueError("Reminder must not follow the task due date")
        else:
            if (
                self.recurrence is not None
                or self.monthly_on_last_day
                or self.recurrence_until is not None
            ):
                raise ValueError("Only events can recur")
            self.start_at = self.end_at = self.start_date = None
            self.due_at = self.due_date = None
            self.reminder_at = None
            self.all_day = False
        has_schedule = self.start_at or self.start_date or self.due_at or self.due_date
        if self.kind != "note" and has_schedule and self.reminder_at is None:
            raise ValueError("Dated events and tasks require a reminder")
        return self


class ExtractionResult(BaseModel):
    items: list[ItemDraft] = Field(min_length=1, max_length=20)


class IntakeItemDraft(ItemDraft):
    owner_id: str | None = Field(
        default=None,
        description="Suggested family member ID, or null when nobody is a clear fit",
    )
    preparation: str | None = Field(
        default=None,
        max_length=500,
        description="One useful preparation step, or null when none is needed",
    )

    @model_validator(mode="after")
    def notes_have_no_owner_or_preparation(self) -> IntakeItemDraft:
        if self.kind == "note":
            self.owner_id = None
            self.preparation = None
        return self


class IntakeAnalysis(BaseModel):
    status: Literal["clarify", "review"]
    message: str = Field(min_length=1, max_length=1000)
    assumptions: list[str] = Field(default_factory=list, max_length=5)
    items: list[IntakeItemDraft] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def match_status(self) -> IntakeAnalysis:
        if self.status == "clarify" and self.items:
            raise ValueError("Clarification responses cannot contain item drafts")
        if self.status == "review" and not self.items:
            raise ValueError("Review responses require at least one item draft")
        return self


class IngestionState(TypedDict, total=False):
    command: dict
    drafts: list[dict]
    result: dict


@lru_cache(maxsize=1)
def openrouter_model():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENROUTER_API_KEY is not configured")
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        temperature=0,
        default_headers={"X-OpenRouter-Title": "Home Orchestrator"},
    )


@lru_cache(maxsize=1)
def openrouter_chain():
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
- For every dated event or task, return one reminder_at as a concrete timezone-aware datetime.
  If the input specifies one, resolve it exactly. Otherwise choose a sensible advance reminder
  from the item's urgency and timing. Do not create a reminder for an item with no date or time.
- Never invent a date, time, owner, or assignee, except for the requested reminder time.
- Keep each title concise and put remaining useful text in details.

{format_instructions}""",
            ),
            (
                "human",
                "Current time: {now}\nTimezone: {timezone_name}\nInput: {text}",
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | openrouter_model() | parser


async def parse_with_openrouter(
    text: str, now: str, timezone_name: str
) -> ExtractionResult:
    return await openrouter_chain().ainvoke(
        {"text": text, "now": now, "timezone_name": timezone_name}
    )


@lru_cache(maxsize=1)
def intake_chain():
    parser = PydanticOutputParser(pydantic_object=IntakeAnalysis)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a concise bilingual household intake assistant. Analyze the
conversation before anything is saved.

Ask one short clarification question only when the answer materially changes the
item type, date, time, recurrence, or prevents a clear contradiction. Never ask
for optional details, reminders, or an owner. At most two clarification questions
are allowed; when Remaining questions is 0, return review with clearly stated
assumptions. If the user says to continue or use your best judgment, return review.

For review:
- Split independent events, tasks, and notes into separate items.
- Preserve the user's language in messages, titles, details, preparation, and assumptions.
- For each event or task, set preparation to one short, concrete preparation
  step only when it is genuinely useful; otherwise set it to null. Never add one
  to notes or turn it into a separate task.
- owner_id must be one listed member ID or null. Prefer an explicitly named person,
  then a clearly relevant household role or established responsibility. Otherwise
  leave it null. Never assign notes. Do not use gender stereotypes.
- If Preferred owner is set, use it for every event or task.
- Resolve relative dates from Current time and Timezone.
- Use date-only fields when no time was stated.
- Only events recur, limited to daily, weekly, or monthly.
- Preserve fixed day-of-month versus month-end recurrence.
- Give every dated event or task a sensible reminder_at unless one was stated.
- Never invent a date or time.

{format_instructions}""",
            ),
            (
                "human",
                """Current time: {now}
Timezone: {timezone_name}
Remaining questions: {remaining_questions}
Preferred owner: {preferred_owner}
Family members and open workload: {family}
Conversation:
{conversation}""",
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | openrouter_model() | parser


async def analyze_intake_with_openrouter(
    conversation: str,
    now: str,
    timezone_name: str,
    remaining_questions: int,
    preferred_owner: str,
    family: str,
) -> IntakeAnalysis:
    return await intake_chain().ainvoke(
        {
            "conversation": conversation,
            "now": now,
            "timezone_name": timezone_name,
            "remaining_questions": remaining_questions,
            "preferred_owner": preferred_owner,
            "family": family,
        }
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

    def _family_context(self) -> str:
        board = self.database.get_board(self.household_id)
        open_counts = {
            member["id"]: sum(
                item["owner_id"] == member["id"]
                and item["kind"] != "note"
                and item["status"] != "done"
                for item in board["items"]
            )
            for member in board["members"]
        }
        return "\n".join(
            f'- id={member["id"]}, name={member["name"]}, '
            f'role={member["role"] or "unspecified"}, open_items={open_counts[member["id"]]}'
            for member in board["members"]
        ) or "No family members"

    async def intake(self, command: dict) -> dict:
        async with self._lock:
            actor_id = self.database.require_member(
                self.household_id, command.get("actor_id")
            )
            text = command.get("text", "").strip()
            if not text:
                raise ValueError("Message cannot be empty")
            session_id = command.get("session_id")
            if session_id:
                session = self.database.add_intake_message(
                    self.household_id, session_id, actor_id, "user", text
                )
            else:
                session = self.database.create_intake_session(
                    self.household_id,
                    actor_id,
                    command.get("owner_id"),
                    command.get("source", "text"),
                    command.get("timezone", "UTC"),
                    text,
                )
            if session["status"] == "review":
                raise ValueError("Confirm or start over before sending another message")
            try:
                local_now = datetime.now(ZoneInfo(session["timezone"]))
            except ZoneInfoNotFoundError as exc:
                raise ValueError("Invalid timezone") from exc
            conversation = "\n".join(
                f'{message["role"]}: {message["content"]}'
                for message in session["messages"]
            )
            analysis = await analyze_intake_with_openrouter(
                conversation=conversation,
                now=local_now.isoformat(),
                timezone_name=session["timezone"],
                remaining_questions=max(0, 2 - session["clarification_count"]),
                preferred_owner=session["owner_id"] or "none",
                family=self._family_context(),
            )
            if session["clarification_count"] >= 2 and analysis.status == "clarify":
                extraction = await parse_with_openrouter(
                    conversation, local_now.isoformat(), session["timezone"]
                )
                chinese = any("\u4e00" <= character <= "\u9fff" for character in text)
                analysis = IntakeAnalysis(
                    status="review",
                    message=(
                        "我会按目前的信息整理，请确认下面的内容。"
                        if chinese else
                        "I used the information available. Please review the items below."
                    ),
                    assumptions=[
                        "未明确的信息保持为空。"
                        if chinese else
                        "Unspecified information was left blank."
                    ],
                    items=[
                        IntakeItemDraft.model_validate(item.model_dump())
                        for item in extraction.items
                    ],
                )
            valid_members = {
                member["id"] for member in self.database.get_board(self.household_id)["members"]
            }
            drafts = []
            for item in analysis.items:
                draft = item.model_dump(mode="json")
                if session["owner_id"] and item.kind != "note":
                    draft["owner_id"] = session["owner_id"]
                elif draft.get("owner_id") not in valid_members:
                    draft["owner_id"] = None
                drafts.append(draft)
            conflicts = (
                self.database.find_draft_conflicts(
                    self.household_id, drafts, session["timezone"]
                )
                if drafts else []
            )
            payload = {
                "message": analysis.message,
                "assumptions": analysis.assumptions,
                "drafts": drafts,
                "conflicts": conflicts,
            }
            status = "clarifying" if analysis.status == "clarify" else "review"
            clarification_count = session["clarification_count"] + (
                analysis.status == "clarify"
            )
            self.database.add_intake_message(
                self.household_id,
                session["id"],
                actor_id,
                "assistant",
                analysis.message,
            )
            session = self.database.update_intake_session(
                self.household_id,
                session["id"],
                actor_id,
                status,
                clarification_count,
                payload,
            )
            return self._intake_response(session)

    def _intake_response(self, session: dict) -> dict:
        return {
            "session_id": session["id"],
            "status": session["status"],
            "messages": session["messages"],
            **session["payload"],
        }

    async def confirm_intake(
        self,
        session_id: str,
        actor_id: str,
        owner_ids: list[str | None],
        accepted_preparations: list[bool],
    ) -> dict:
        async with self._lock:
            session = self.database.get_intake_session(
                self.household_id, session_id, actor_id
            )
            drafts = session["payload"].get("drafts") or []
            if len(owner_ids) != len(drafts):
                raise ValueError("Choose an owner or no owner for every draft")
            if len(accepted_preparations) != len(drafts):
                raise ValueError("Accept or reject preparation for every draft")
            valid_members = {
                member["id"] for member in self.database.get_board(self.household_id)["members"]
            }
            for draft, owner_id, accepted in zip(
                drafts, owner_ids, accepted_preparations
            ):
                if owner_id is not None and owner_id not in valid_members:
                    raise ValueError("Choose a valid family member")
                draft["owner_id"] = owner_id if draft["kind"] != "note" else None
                if not accepted or draft["kind"] == "note":
                    draft["preparation"] = None
            session["payload"]["drafts"] = drafts
            self.database.update_intake_session(
                self.household_id,
                session_id,
                actor_id,
                session["status"],
                session["clarification_count"],
                session["payload"],
            )
            result = self.database.confirm_intake_session(
                self.household_id, session_id, actor_id
            )
            return await self.get_board(result)

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
