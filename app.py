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
from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from supabase import create_client
from supabase_auth.errors import AuthError

from board_db import BoardDatabase
from board_graph import BoardService, ConfigurationError
from weather import (
    WeatherConfigurationError,
    WeatherProviderError,
    WeatherService,
)

load_dotenv()

ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"
MAX_AUDIO_BYTES = 10 * 1024 * 1024
ACCESS_COOKIE = "hearthbook_access"
REFRESH_COOKIE = "hearthbook_refresh"
HOUSEHOLD_COOKIE = "hearthbook_household"
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_url = os.getenv("DATABASE_URL", "")
    app.state.supabase_url = os.getenv("SUPABASE_URL", "")
    app.state.supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if not all(
        (
            app.state.database_url,
            app.state.supabase_url,
            app.state.supabase_key,
        )
    ):
        raise RuntimeError(
            "DATABASE_URL, SUPABASE_URL, and SUPABASE_PUBLISHABLE_KEY are required"
        )
    app.state.weather = WeatherService(os.getenv("OPENWEATHER_API_KEY"))
    yield


app = FastAPI(title="Home Orchestrator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def require_supabase_session(request: Request, call_next):
    path = request.url.path
    if not path.startswith("/api/") or path.startswith("/api/auth/"):
        return await call_next(request)

    authenticated = authenticate(request)
    if authenticated is None:
        return JSONResponse({"detail": "Authentication required"}, status_code=401)
    user, access_token, refreshed_session = authenticated
    request.state.user_id = str(user.id)
    request.state.access_token = access_token

    client = data_client(request, access_token)
    membership_response = (
        client.table("household_memberships")
        .select("household_id")
        .eq("user_id", str(user.id))
        .execute()
    )
    household_ids = [
        membership["household_id"]
        for membership in membership_response.data or []
    ]
    requested_household_id = request.cookies.get(HOUSEHOLD_COOKIE)
    request.state.household_id = (
        requested_household_id
        if requested_household_id in household_ids
        else household_ids[0] if household_ids else None
    )
    if request.state.household_id is None and path not in {
        "/api/households",
        "/api/households/join",
    }:
        return JSONResponse(
            {"detail": "Household setup required"}, status_code=409
        )

    try:
        response = await call_next(request)
    finally:
        database = getattr(request.state, "database", None)
        if database is not None:
            database.close()
    if refreshed_session is not None:
        set_auth_cookies(response, refreshed_session, request)
    return response


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


class AuthInput(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class HouseholdCreateInput(BaseModel):
    household_name: str = Field(min_length=1, max_length=80)
    member_name: str = Field(min_length=1, max_length=40)


class HouseholdJoinInput(BaseModel):
    invite_code: str = Field(min_length=1, max_length=40)
    member_name: str = Field(min_length=1, max_length=40)


class HouseholdSelectInput(BaseModel):
    household_id: str = Field(min_length=1, max_length=80)


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
    preparation: str | None = Field(default=None, max_length=500)
    start_at: datetime | None = None
    end_at: datetime | None = None
    start_date: date | None = None


def board_service(request: Request) -> BoardService:
    database = getattr(request.state, "database", None)
    if database is None:
        database = BoardDatabase(
            request.app.state.database_url, request.state.user_id
        )
        request.state.database = database
    return BoardService(database, request.state.household_id)


def weather_service(request: Request) -> WeatherService:
    return request.app.state.weather


def auth_client(request: Request):
    return create_client(
        request.app.state.supabase_url, request.app.state.supabase_key
    )


def data_client(request: Request, access_token: str):
    client = auth_client(request)
    client.postgrest.auth(access_token)
    return client


def authenticate(request: Request):
    access_token = request.cookies.get(ACCESS_COOKIE)
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    client = auth_client(request)
    if access_token:
        try:
            user = client.auth.get_user(access_token).user
            if user is not None:
                return user, access_token, None
        except AuthError:
            pass
    if not refresh_token:
        return None
    try:
        refreshed = client.auth.refresh_session(refresh_token)
    except AuthError:
        return None
    if refreshed.user is None or refreshed.session is None:
        return None
    return refreshed.user, refreshed.session.access_token, refreshed.session


def set_auth_cookies(response: Response, session, request: Request) -> None:
    secure = request.url.scheme == "https"
    response.set_cookie(
        ACCESS_COOKIE,
        session.access_token,
        max_age=session.expires_in,
        httponly=True,
        secure=secure,
        samesite="lax",
    )
    response.set_cookie(
        REFRESH_COOKIE,
        session.refresh_token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=secure,
        samesite="lax",
    )


def set_household_cookie(
    response: Response, household_id: str, request: Request
) -> None:
    response.set_cookie(
        HOUSEHOLD_COOKIE,
        household_id,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )


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


@app.post("/api/auth/signup")
async def signup(payload: AuthInput, request: Request, response: Response):
    try:
        result = auth_client(request).auth.sign_up(
            {"email": payload.email.strip(), "password": payload.password}
        )
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result.session is not None:
        set_auth_cookies(response, result.session, request)
    return {
        "authenticated": result.session is not None,
        "confirmation_required": result.session is None,
    }


@app.post("/api/auth/login")
async def login(payload: AuthInput, request: Request, response: Response):
    try:
        result = auth_client(request).auth.sign_in_with_password(
            {"email": payload.email.strip(), "password": payload.password}
        )
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="Invalid email or password") from exc
    if result.session is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    set_auth_cookies(response, result.session, request)
    return {"authenticated": True}


@app.get("/api/auth/session")
async def get_session(request: Request, response: Response):
    authenticated = authenticate(request)
    if authenticated is None:
        return {"authenticated": False, "household_ready": False}
    user, access_token, refreshed_session = authenticated
    if refreshed_session is not None:
        set_auth_cookies(response, refreshed_session, request)
    client = data_client(request, access_token)
    membership_response = (
        client
        .table("household_memberships")
        .select("household_id")
        .eq("user_id", str(user.id))
        .execute()
    )
    household_ids = [
        membership["household_id"]
        for membership in membership_response.data or []
    ]
    household_response = (
        client.table("households")
        .select("id,name")
        .in_("id", household_ids)
        .execute()
        if household_ids
        else None
    )
    households = household_response.data if household_response else []
    requested_household_id = request.cookies.get(HOUSEHOLD_COOKIE)
    active_household_id = (
        requested_household_id
        if requested_household_id in household_ids
        else household_ids[0] if household_ids else None
    )
    if active_household_id and active_household_id != requested_household_id:
        set_household_cookie(response, active_household_id, request)
    return {
        "authenticated": True,
        "email": user.email,
        "household_ready": bool(households),
        "households": households,
        "active_household_id": active_household_id,
    }


@app.delete("/api/auth/session")
async def delete_session(response: Response):
    response.delete_cookie(ACCESS_COOKIE, httponly=True, samesite="lax")
    response.delete_cookie(REFRESH_COOKIE, httponly=True, samesite="lax")
    response.delete_cookie(HOUSEHOLD_COOKIE, httponly=True, samesite="lax")
    return {"authenticated": False}


@app.post("/api/households", status_code=201)
async def create_household(
    payload: HouseholdCreateInput, request: Request, response: Response
):
    try:
        result = data_client(request, request.state.access_token).rpc(
            "create_household",
            {
                "household_name": payload.household_name,
                "member_name": payload.member_name,
            },
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    set_household_cookie(response, result.data, request)
    return {"created": True, "household_id": result.data}


@app.post("/api/households/join")
async def join_household(
    payload: HouseholdJoinInput, request: Request, response: Response
):
    try:
        result = data_client(request, request.state.access_token).rpc(
            "join_household",
            {
                "household_invite_code": payload.invite_code,
                "member_name": payload.member_name,
            },
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    set_household_cookie(response, result.data, request)
    return {"joined": True, "household_id": result.data}


@app.post("/api/households/select")
async def select_household(
    payload: HouseholdSelectInput, request: Request, response: Response
):
    membership = (
        data_client(request, request.state.access_token)
        .table("household_memberships")
        .select("household_id")
        .eq("user_id", request.state.user_id)
        .eq("household_id", payload.household_id)
        .maybe_single()
        .execute()
    )
    if membership is None or membership.data is None:
        raise HTTPException(status_code=404, detail="Household not found")
    set_household_cookie(response, payload.household_id, request)
    return {"selected": True}


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
    port = os.getenv("PORT")
    uvicorn.run(
        "app:app",
        host="0.0.0.0" if port else "127.0.0.1",
        port=int(port or 8000),
        reload=not port,
    )


if __name__ == "__main__":
    main()
