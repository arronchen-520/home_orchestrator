from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api_utils import service_call
from dependencies import board_service, weather_service
from weather import WeatherConfigurationError, WeatherProviderError

router = APIRouter(prefix="/api")


class HouseholdLocationInput(BaseModel):
    city: str = Field(min_length=2, max_length=120)


class MemberInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    role: str = Field(default="", max_length=40)


class ItemUpdate(BaseModel):
    actor_id: str
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    remind_member_id: str | None = None
    completed: bool | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None
    due_at: datetime | None = None
    due_date: date | None = None
    reminder_at: datetime | None = None
    all_day: bool | None = None
    recurrence_until: date | None = None


class ItemNoteInput(BaseModel):
    actor_id: str
    content: str = Field(min_length=1, max_length=1000)


class OccurrenceUpdate(BaseModel):
    actor_id: str
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None


async def execute(request: Request, command: dict):
    return await service_call(board_service(request).execute(command))


@router.get("/board")
async def board(request: Request):
    return await board_service(request).get_board()


@router.get("/today")
async def today(request: Request, target: date = Query(alias="date"), timezone: str = "UTC"):
    try:
        return board_service(request).get_today(target, timezone)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/calendar")
async def calendar(start: date, end: date, request: Request):
    try:
        return board_service(request).get_calendar(start, end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/household")
async def set_household_location(payload: HouseholdLocationInput, request: Request):
    try:
        location = await weather_service(request).geocode(payload.city)
        result = await board_service(request).set_household_location(location)
        weather_service(request).clear_cache()
        return result
    except WeatherConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except WeatherProviderError as exc:
        raise HTTPException(status_code=502, detail="The weather service is unavailable") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/weather")
async def weather(request: Request, lang: Literal["en", "zh_cn"] = "en"):
    location = board_service(request).get_weather_location()
    if location is None:
        raise HTTPException(status_code=400, detail="Choose a household city first")
    try:
        return await weather_service(request).forecast(location, lang)
    except WeatherConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except WeatherProviderError as exc:
        raise HTTPException(status_code=502, detail="The weather service is unavailable") from exc


@router.post("/members", status_code=201)
async def add_member(payload: MemberInput, request: Request):
    return await execute(request, {"type": "add_member", "name": payload.name, "role": payload.role})


@router.delete("/members/{member_id}")
async def delete_member(member_id: str, request: Request):
    return await execute(request, {"type": "delete_member", "member_id": member_id})


@router.patch("/items/{item_id}")
async def update_item(item_id: str, payload: ItemUpdate, request: Request):
    fields = payload.model_dump(mode="json", include=payload.model_fields_set - {"actor_id"}, exclude_none=False)
    return await execute(request, {"type": "update_item", "item_id": item_id, "actor_id": payload.actor_id, "fields": fields})


@router.post("/items/{item_id}/notes", status_code=201)
async def add_item_note(item_id: str, payload: ItemNoteInput, request: Request):
    return await execute(request, {"type": "add_item_note", "item_id": item_id, "actor_id": payload.actor_id, "content": payload.content})


@router.patch("/items/{item_id}/occurrences/{occurrence_date}")
async def update_occurrence(item_id: str, occurrence_date: date, payload: OccurrenceUpdate, request: Request):
    fields = payload.model_dump(mode="json", include=payload.model_fields_set - {"actor_id"}, exclude_none=False)
    return await execute(request, {"type": "update_occurrence", "item_id": item_id, "occurrence_date": occurrence_date.isoformat(), "actor_id": payload.actor_id, "fields": fields})


@router.delete("/items/{item_id}/occurrences/{occurrence_date}")
async def cancel_occurrence(item_id: str, occurrence_date: date, actor_id: str, request: Request):
    return await execute(request, {"type": "cancel_occurrence", "item_id": item_id, "occurrence_date": occurrence_date.isoformat(), "actor_id": actor_id})


@router.delete("/items/{item_id}")
async def delete_item(item_id: str, actor_id: str, request: Request):
    return await execute(request, {"type": "delete_item", "item_id": item_id, "actor_id": actor_id})
