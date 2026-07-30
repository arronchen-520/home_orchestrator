from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel, Field

from board_graph import BoardService, ConfigurationError

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
MAX_AUDIO_BYTES = 10 * 1024 * 1024
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    DATA_DIR.mkdir(exist_ok=True)
    database = Path(os.getenv("BOARD_DB_PATH", DATA_DIR / "board.sqlite3"))
    if not database.is_absolute():
        database = ROOT / database
    database.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(database)) as saver:
        await saver.setup()
        app.state.board = BoardService(
            saver, os.getenv("HOUSEHOLD_ID", "family-default")
        )
        yield


app = FastAPI(title="Home Orchestrator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class TextInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    actor_id: str
    owner_id: str | None = None
    timezone: str = "UTC"


class MemberInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class ItemUpdate(BaseModel):
    actor_id: str
    owner_id: str | None = None
    status: Literal["unclaimed", "claimed", "done"] | None = None


def board_service(request: Request) -> BoardService:
    return request.app.state.board


async def execute(service: BoardService, command: dict) -> dict:
    try:
        return await service.execute(command)
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


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/board")
async def get_board(request: Request):
    return await board_service(request).get_board()


@app.post("/api/members", status_code=201)
async def add_member(payload: MemberInput, request: Request):
    return await execute(
        board_service(request), {"type": "add_member", "name": payload.name}
    )


@app.post("/api/input", status_code=201)
async def add_text(payload: TextInput, request: Request):
    return await execute(
        board_service(request),
        {
            "type": "add_item",
            "text": payload.text.strip(),
            "actor_id": payload.actor_id,
            "owner_id": payload.owner_id,
            "timezone": payload.timezone,
        },
    )


@app.post("/api/audio", status_code=201)
async def add_audio(
    request: Request,
    file: Annotated[UploadFile, File()],
    actor_id: Annotated[str, Form()],
    timezone_name: Annotated[str, Form(alias="timezone")],
    owner_id: Annotated[str | None, Form()] = None,
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

    return await execute(
        board_service(request),
        {
            "type": "add_item",
            "text": text,
            "actor_id": actor_id,
            "owner_id": owner_id or None,
            "timezone": timezone_name,
        },
    )


@app.patch("/api/items/{item_id}")
async def update_item(item_id: str, payload: ItemUpdate, request: Request):
    fields = payload.model_dump(
        include=payload.model_fields_set - {"actor_id"}, exclude_none=False
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
