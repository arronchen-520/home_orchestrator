from __future__ import annotations

import logging
import os
from typing import Annotated

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from api_utils import service_call
from dependencies import board_service

MAX_AUDIO_BYTES = 10 * 1024 * 1024
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class MessageInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    actor_id: str
    timezone: str = "UTC"
    session_id: str | None = None


class CaptureConfirmation(BaseModel):
    actor_id: str
    remind_member_ids: list[str | None] = Field(max_length=20)
    accepted_preparations: list[bool] = Field(max_length=20)


@router.post("/messages")
async def message(payload: MessageInput, request: Request):
    return await service_call(board_service(request).message(payload.model_dump()))


@router.post("/conversations/{session_id}/confirm", status_code=201)
async def confirm(session_id: str, payload: CaptureConfirmation, request: Request):
    return await service_call(
        board_service(request).confirm_capture(
            session_id, payload.actor_id, payload.remind_member_ids, payload.accepted_preparations
        )
    )


async def transcribe(file: UploadFile) -> str:
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="DEEPGRAM_API_KEY is not configured")
    if not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=415, detail="Upload an audio file")
    audio = await file.read(MAX_AUDIO_BYTES + 1)
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio must be 10 MB or smaller")
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                params={"model": os.getenv("DEEPGRAM_MODEL", "nova-2"), "language": "multi", "smart_format": "true"},
                headers={"Authorization": f"Token {api_key}", "Content-Type": file.content_type or "audio/webm"},
                content=audio,
            )
            response.raise_for_status()
            return response.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "").strip()
    except (httpx.HTTPError, ValueError, IndexError) as exc:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=502, detail="Transcription failed") from exc


@router.post("/audio")
async def audio_message(
    request: Request,
    file: Annotated[UploadFile, File()],
    actor_id: Annotated[str, Form()],
    timezone: Annotated[str, Form()] = "UTC",
    session_id: Annotated[str | None, Form()] = None,
):
    text = await transcribe(file)
    if not text:
        raise HTTPException(status_code=422, detail="No speech was detected")
    result = await service_call(
        board_service(request).message({"text": text, "actor_id": actor_id, "timezone": timezone, "session_id": session_id})
    )
    return {**result, "transcript": text}
