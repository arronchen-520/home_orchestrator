from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Literal

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from board_db import BoardDatabase
from board_graph import BoardService, ConfigurationError
from weather import (
    WeatherConfigurationError,
    WeatherProviderError,
    WeatherService,
)

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
MAX_AUDIO_BYTES = 10 * 1024 * 1024
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    DATA_DIR.mkdir(exist_ok=True)
    database_path = Path(os.getenv("BOARD_DB_PATH", DATA_DIR / "board.sqlite3"))
    if not database_path.is_absolute():
        database_path = ROOT / database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database = BoardDatabase(database_path)
    database.setup()
    household_id = os.getenv("HOUSEHOLD_ID", "family-default")
    app.state.board = BoardService(database, household_id)
    app.state.weather = WeatherService(os.getenv("OPENWEATHER_API_KEY"))
    try:
        yield
    finally:
        database.close()


app = FastAPI(title="Home Orchestrator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class TextInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    actor_id: str
    owner_id: str | None = None
    timezone: str = "UTC"
    session_id: str | None = None


class IntakeConfirmation(BaseModel):
    actor_id: str
    owner_ids: list[str | None] = Field(max_length=20)
    accepted_preparations: list[bool] = Field(max_length=20)


class AssistantInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    actor_id: str
    timezone: str = "UTC"
    session_id: str | None = None


class MemberInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    role: str = Field(default="", max_length=40)


class HouseholdLocationInput(BaseModel):
    city: str = Field(min_length=2, max_length=120)


class ItemUpdate(BaseModel):
    actor_id: str
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    preparation: str | None = Field(default=None, max_length=500)
    owner_id: str | None = None
    status: Literal["unclaimed", "claimed", "done"] | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None
    due_at: datetime | None = None
    due_date: date | None = None
    reminder_at: datetime | None = None
    all_day: bool | None = None
    recurrence_until: date | None = None


class AssignmentResponse(BaseModel):
    actor_id: str
    accept: bool


class OccurrenceUpdate(BaseModel):
    actor_id: str
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None


def board_service(request: Request) -> BoardService:
    return request.app.state.board


def weather_service(request: Request) -> WeatherService:
    return request.app.state.weather


async def service_call(awaitable) -> dict:
    try:
        return await awaitable
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Board command failed")
        raise HTTPException(
            status_code=502,
            detail="The AI service could not process this input.",
        ) from exc


async def execute(service: BoardService, command: dict) -> dict:
    return await service_call(service.execute(command))


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/board")
async def get_board(request: Request):
    return await board_service(request).get_board()


@app.get("/api/calendar")
async def get_calendar(start: date, end: date, request: Request):
    try:
        return await board_service(request).get_calendar(start, end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/household")
async def set_household_location(
    payload: HouseholdLocationInput, request: Request
):
    try:
        location = await weather_service(request).geocode(payload.city)
        board = await board_service(request).set_household_location(location)
        weather_service(request).clear_cache()
        return board
    except WeatherConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=502, detail="The weather service is unavailable"
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/weather")
async def get_weather(request: Request, lang: Literal["en", "zh_cn"] = "en"):
    location = board_service(request).get_weather_location()
    if location is None:
        raise HTTPException(status_code=400, detail="Choose a household city first")
    try:
        return await weather_service(request).forecast(location, lang)
    except WeatherConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=502, detail="The weather service is unavailable"
        ) from exc


@app.post("/api/members", status_code=201)
async def add_member(payload: MemberInput, request: Request):
    return await execute(
        board_service(request), {"type": "add_member", "name": payload.name, "role": payload.role}
    )


@app.delete("/api/members/{member_id}")
async def delete_member(member_id: str, request: Request):
    return await execute(
        board_service(request), {"type": "delete_member", "member_id": member_id}
    )


@app.post("/api/input", status_code=201)
async def add_text(payload: TextInput, request: Request):
    return await service_call(
        board_service(request).intake(
            {
                "text": payload.text.strip(),
                "actor_id": payload.actor_id,
                "owner_id": payload.owner_id,
                "timezone": payload.timezone,
                "source": "text",
                "session_id": payload.session_id,
            }
        )
    )


@app.post("/api/intake/{session_id}/confirm", status_code=201)
async def confirm_intake(
    session_id: str, payload: IntakeConfirmation, request: Request
):
    return await service_call(
        board_service(request).confirm_intake(
            session_id,
            payload.actor_id,
            payload.owner_ids,
            payload.accepted_preparations,
        )
    )


@app.post("/api/assistant")
async def assistant(payload: AssistantInput, request: Request):
    return await service_call(
        board_service(request).assistant(
            {
                "text": payload.text.strip(),
                "actor_id": payload.actor_id,
                "timezone": payload.timezone,
                "session_id": payload.session_id,
            }
        )
    )


@app.post("/api/audio", status_code=201)
async def add_audio(
    request: Request,
    file: Annotated[UploadFile, File()],
    actor_id: Annotated[str, Form()],
    timezone_name: Annotated[str, Form(alias="timezone")],
    owner_id: Annotated[str | None, Form()] = None,
    session_id: Annotated[str | None, Form()] = None,
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured")
    if not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=415, detail="Upload an audio file")

    audio = await file.read(MAX_AUDIO_BYTES + 1)
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio must be 10 MB or smaller")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={
                    "model": os.getenv(
                        "GROQ_STT_MODEL", "whisper-large-v3-turbo"
                    ),
                    "response_format": "json",
                },
                files={
                    "file": (
                        file.filename or "recording.webm",
                        audio,
                        file.content_type,
                    )
                },
            )
            response.raise_for_status()
            text = response.json().get("text", "").strip()
    except (httpx.HTTPError, ValueError) as exc:
        logger.exception("Groq transcription failed")
        raise HTTPException(status_code=502, detail="Transcription failed") from exc

    if not text:
        raise HTTPException(status_code=422, detail="No speech was detected")

    return await service_call(
        board_service(request).intake(
            {
                "text": text,
                "actor_id": actor_id,
                "owner_id": owner_id or None,
                "timezone": timezone_name,
                "source": "audio",
                "session_id": session_id,
            }
        )
    )


@app.patch("/api/items/{item_id}")
async def update_item(item_id: str, payload: ItemUpdate, request: Request):
    fields = payload.model_dump(
        mode="json",
        include=payload.model_fields_set - {"actor_id"},
        exclude_none=False,
    )
    return await execute(
        board_service(request),
        {
            "type": "update_item",
            "item_id": item_id,
            "actor_id": payload.actor_id,
            "fields": fields,
        },
    )


@app.post("/api/items/{item_id}/assignment")
async def respond_to_assignment(
    item_id: str, payload: AssignmentResponse, request: Request
):
    return await execute(
        board_service(request),
        {
            "type": "respond_to_task_assignment",
            "item_id": item_id,
            "actor_id": payload.actor_id,
            "accept": payload.accept,
        },
    )


@app.patch("/api/items/{item_id}/occurrences/{occurrence_date}")
async def update_occurrence(
    item_id: str,
    occurrence_date: date,
    payload: OccurrenceUpdate,
    request: Request,
):
    fields = payload.model_dump(
        mode="json",
        include=payload.model_fields_set - {"actor_id"},
        exclude_none=False,
    )
    return await execute(
        board_service(request),
        {
            "type": "update_occurrence",
            "item_id": item_id,
            "occurrence_date": occurrence_date.isoformat(),
            "actor_id": payload.actor_id,
            "fields": fields,
        },
    )


@app.delete("/api/items/{item_id}/occurrences/{occurrence_date}")
async def cancel_occurrence(
    item_id: str, occurrence_date: date, actor_id: str, request: Request
):
    return await execute(
        board_service(request),
        {
            "type": "cancel_occurrence",
            "item_id": item_id,
            "occurrence_date": occurrence_date.isoformat(),
            "actor_id": actor_id,
        },
    )


@app.delete("/api/items/{item_id}")
async def delete_item(item_id: str, actor_id: str, request: Request):
    return await execute(
        board_service(request),
        {"type": "delete_item", "item_id": item_id, "actor_id": actor_id},
    )


def main():
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
