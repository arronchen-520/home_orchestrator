from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, model_validator

ItemKind = Literal["event", "task", "note"]
Intent = Literal["capture", "query", "chat"]
Recurrence = Literal["daily", "weekly", "monthly"]
Weekday = Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
WEEKDAYS = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
MAX_REMINDER_RECIPIENTS = 5


class ItemDraft(BaseModel):
    kind: ItemKind
    title: str = Field(min_length=1, max_length=120)
    details: str = Field(default="", max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    remind_member_ids: list[str] = Field(default_factory=list)
    schedule_timezone: str | None = None
    start_at: datetime | None = Field(
        default=None, description="Specific start date and time; do not use for date-only events."
    )
    end_at: datetime | None = Field(
        default=None, description="Specific end date and time, only when an actual end time is known."
    )
    start_date: date | None = Field(
        default=None, description="Date-only event start date; use instead of start_at and end_at."
    )
    end_date: date | None = Field(default=None, description="Inclusive end date for a date-only event.")
    due_at: datetime | None = None
    due_date: date | None = None
    reminder_at: datetime | None = None
    all_day: bool = Field(
        default=False,
        description="True only for a date-only event; use start_date and leave start_at/end_at null.",
    )
    recurrence: Recurrence | None = None
    weekdays: list[Weekday] = Field(default_factory=list)
    monthly_on_last_day: bool = False
    recurrence_until: date | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_event_schedule(cls, value):
        if not isinstance(value, dict) or value.get("kind") != "event":
            return value
        data = dict(value)
        if data.get("start_date"):
            data["all_day"] = True
            data["start_at"] = data["end_at"] = None
            return data
        if not data.get("all_day") or not data.get("start_at"):
            return data
        try:
            start = data["start_at"] if isinstance(data["start_at"], datetime) else datetime.fromisoformat(str(data["start_at"]))
            end = data.get("end_at")
            end = end if isinstance(end, datetime) else datetime.fromisoformat(str(end)) if end else None
        except (TypeError, ValueError):
            return data
        if (
            start.hour == start.minute == start.second == start.microsecond == 0
            and end is not None
            and end.hour == 23
            and end.minute == 59
            and end.second == 59
            and end.microsecond == 0
        ):
            data["start_date"] = start.date()
            data["end_date"] = end.date() if end.date() != start.date() else None
            data["start_at"] = data["end_at"] = None
        else:
            data["all_day"] = False
        return data

    @model_validator(mode="after")
    def match_kind(self) -> "ItemDraft":
        for value in (self.start_at, self.end_at, self.due_at, self.reminder_at):
            if value is not None and value.utcoffset() is None:
                raise ValueError("Date-times require a timezone")
        if self.schedule_timezone:
            try:
                ZoneInfo(self.schedule_timezone)
            except ZoneInfoNotFoundError as exc:
                raise ValueError("Invalid schedule timezone") from exc
        if self.kind == "event":
            self.due_at = self.due_date = None
            first = self.start_date or (self.start_at.date() if self.start_at else None)
            if self.start_date:
                self.all_day = True
            if self.all_day:
                if not self.start_date:
                    raise ValueError("An all-day event requires a date")
                self.start_at = self.end_at = None
                if self.end_date and self.end_date < self.start_date:
                    raise ValueError("Event end date must not precede its start")
            else:
                self.end_date = None
                if not self.start_at:
                    raise ValueError("A timed event requires a start")
                if self.end_at and self.end_at < self.start_at:
                    raise ValueError("Event end must be after its start")
            if self.monthly_on_last_day:
                if self.recurrence != "monthly":
                    raise ValueError("Last-day recurrence must be monthly")
                if first and first.day != monthrange(first.year, first.month)[1]:
                    raise ValueError("Last-day recurrence must start on a month's last day")
            self.weekdays = sorted(set(self.weekdays), key=WEEKDAYS.index)
            if self.weekdays and self.recurrence != "weekly":
                raise ValueError("Weekdays require weekly recurrence")
            if self.recurrence_until:
                if not self.recurrence:
                    raise ValueError("A recurrence end date requires recurrence")
                if first and self.recurrence_until < first:
                    raise ValueError("Recurrence end date cannot precede its start")
        elif self.kind == "task":
            if self.recurrence or self.weekdays or self.monthly_on_last_day or self.recurrence_until:
                raise ValueError("Only events can recur")
            self.start_at = self.end_at = self.start_date = self.end_date = None
            self.all_day = False
            if self.due_at and self.due_date:
                raise ValueError("A task cannot have both a due date and due time")
        else:
            self.start_at = self.end_at = self.start_date = self.end_date = None
            self.due_at = self.due_date = self.reminder_at = None
            self.preparation = self.schedule_timezone = None
            self.remind_member_ids = []
            self.recurrence = self.recurrence_until = None
            self.weekdays = []
            self.monthly_on_last_day = self.all_day = False
        return self


class RouteDecision(BaseModel):
    intent: Intent


class CaptureAnalysis(BaseModel):
    status: Literal["clarify", "review"]
    message: str = Field(default="", max_length=1000)
    items: list[ItemDraft] = Field(default_factory=list, max_length=20)
    updated_memory: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_capture_output(cls, value):
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if data.get("status") == "clarify" and data.get("items"):
            data["items"] = []
        else:
            data["items"] = [
                {key: field for key, field in item.items() if key != "schedule_timezone"}
                if isinstance(item, dict) else item
                for item in data.get("items", [])
            ]
        return data

    @model_validator(mode="after")
    def match_status(self) -> "CaptureAnalysis":
        if self.status == "clarify":
            if self.items:
                raise ValueError("Clarification cannot include drafts")
            if not self.message.strip():
                raise ValueError("Clarification requires a message")
        elif not self.items:
            raise ValueError("Review requires at least one draft")
        return self


class ProposedUpdate(BaseModel):
    item_id: str
    fields: dict[str, str | bool | list[str] | None]
    confirmation: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def supported_fields(self) -> "ProposedUpdate":
        allowed = {
            "title", "details", "preparation", "remind_member_ids", "completed",
            "start_at", "end_at", "start_date", "end_date", "due_at", "due_date",
            "reminder_at", "schedule_timezone", "all_day", "recurrence", "weekdays",
            "monthly_on_last_day", "recurrence_until",
        }
        if not self.fields or set(self.fields) - allowed:
            raise ValueError("Unsupported proposed update")
        recurrence_fields = {"recurrence", "weekdays", "monthly_on_last_day"}
        field_names = set(self.fields)
        if recurrence_fields & field_names and not recurrence_fields <= field_names:
            raise ValueError("A recurrence update requires a complete rule")
        return self


class AgentReply(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    action: ProposedUpdate | None = None
    references: list[str] = Field(default_factory=list, max_length=20)
    updated_memory: str | None = None


class QueryDecision(AgentReply):
    status: Literal["answer", "needs_details", "clarify"]
