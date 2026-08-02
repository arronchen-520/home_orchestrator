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


class ItemDraft(BaseModel):
    kind: ItemKind
    title: str = Field(min_length=1, max_length=120)
    details: str = Field(default="", max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    remind_member_ids: list[str] = Field(default_factory=list, max_length=20)
    schedule_timezone: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None
    due_at: datetime | None = None
    due_date: date | None = None
    reminder_at: datetime | None = None
    all_day: bool = False
    recurrence: Recurrence | None = None
    weekdays: list[Weekday] = Field(default_factory=list)
    monthly_on_last_day: bool = False
    recurrence_until: date | None = None

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
            elif not self.start_at:
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
            self.start_at = self.end_at = self.start_date = None
            self.all_day = False
            if self.due_at and self.due_date:
                raise ValueError("A task cannot have both a due date and due time")
        else:
            self.start_at = self.end_at = self.start_date = None
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

    @model_validator(mode="after")
    def match_status(self) -> "CaptureAnalysis":
        if self.status == "clarify":
            if self.items:
                raise ValueError("Clarification cannot include drafts")
            if not self.message.strip():
                raise ValueError("Clarification requires a message")
        elif not self.items:
            raise ValueError("Review requires at least one draft")
        elif not self.message.strip():
            self.message = "Please confirm the following."
        return self


class ProposedUpdate(BaseModel):
    item_id: str
    fields: dict[str, str | bool | list[str] | None]
    confirmation: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def supported_fields(self) -> "ProposedUpdate":
        allowed = {
            "title", "details", "preparation", "remind_member_ids", "completed",
            "start_at", "end_at", "start_date", "due_at", "due_date",
            "reminder_at", "schedule_timezone", "all_day", "recurrence_until",
        }
        if not self.fields or set(self.fields) - allowed:
            raise ValueError("Unsupported proposed update")
        return self


class AgentReply(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    action: ProposedUpdate | None = None
    references: list[str] = Field(default_factory=list, max_length=20)
    updated_memory: str | None = None


class QueryDecision(AgentReply):
    status: Literal["answer", "needs_details", "clarify"]
