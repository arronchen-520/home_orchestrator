from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..domain.models import Weekday

from .dependencies import board_service

router = APIRouter(prefix="/api")


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    remind_member_ids: list[str] = Field(default_factory=list, max_length=20)
    completed: bool | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None
    due_at: datetime | None = None
    due_date: date | None = None
    reminder_at: datetime | None = None
    schedule_timezone: str | None = Field(default=None, min_length=1, max_length=100)
    all_day: bool | None = None
    recurrence: Literal["daily", "weekly", "monthly"] | None = None
    weekdays: list[Weekday] | None = None
    monthly_on_last_day: bool | None = None
    recurrence_until: date | None = None


class MemberProfileInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    role: str = Field(default="", max_length=40)


class ItemNoteInput(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class OccurrenceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None


@router.get("/board")
async def board(request: Request):
    return board_service(request).get_board()


@router.get("/today")
async def today(request: Request, target: date = Query(alias="date"), timezone: str = "UTC"):
    try:
        ZoneInfo(timezone)
        return board_service(request).get_today(target, timezone)
    except (ValueError, KeyError, ZoneInfoNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/calendar")
async def calendar(start: date, end: date, request: Request, timezone: str = "UTC"):
    try:
        ZoneInfo(timezone)
        return board_service(request).get_calendar(start, end, timezone)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/members/me")
async def update_my_member_profile(payload: MemberProfileInput, request: Request):
    return board_service(request).update_member_profile(payload.name, payload.role)


@router.patch("/items/{item_id}")
async def update_item(item_id: str, payload: ItemUpdate, request: Request):
    fields = payload.model_dump(
        mode="json", include=payload.model_fields_set, exclude_none=False
    )
    return board_service(request).update_item(item_id, fields)


@router.post("/items/{item_id}/notes", status_code=201)
async def add_item_note(item_id: str, payload: ItemNoteInput, request: Request):
    return board_service(request).add_item_note(item_id, payload.content)


@router.patch("/items/{item_id}/occurrences/{occurrence_date}")
async def update_occurrence(item_id: str, occurrence_date: date, payload: OccurrenceUpdate, request: Request):
    fields = payload.model_dump(
        mode="json", include=payload.model_fields_set, exclude_none=False
    )
    return board_service(request).update_occurrence(item_id, occurrence_date.isoformat(), fields)


@router.delete("/items/{item_id}/occurrences/{occurrence_date}")
async def cancel_occurrence(item_id: str, occurrence_date: date, request: Request):
    return board_service(request).cancel_occurrence(item_id, occurrence_date.isoformat())


@router.delete("/items/{item_id}")
async def delete_item(item_id: str, request: Request):
    return board_service(request).delete_item(item_id)
