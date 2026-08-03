from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, HTTPException, Request
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator
from supabase import Client, create_client

from .errors import request_context

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/notifications")


class PushKeys(BaseModel):
    p256dh: str = Field(min_length=20, max_length=200)
    auth: str = Field(min_length=8, max_length=100)


class PushSubscriptionInput(BaseModel):
    endpoint: AnyHttpUrl
    keys: PushKeys
    timezone: str = Field(min_length=1, max_length=100)
    language: Literal["zh", "en"] = "en"

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Invalid timezone") from exc
        return value


class PushSubscriptionDelete(BaseModel):
    endpoint: AnyHttpUrl


def notification_client(request: Request) -> Client:
    if not request.app.state.supabase_secret_key:
        logger.error("Notifications unavailable reason=missing_configuration %s", request_context(request))
        raise HTTPException(status_code=503, detail={"code": "notifications_unavailable"})
    return create_client(request.app.state.supabase_url, request.app.state.supabase_secret_key)


@router.get("/config")
async def notification_config(request: Request):
    return {
        "enabled": bool(
            request.app.state.vapid_public_key and request.app.state.supabase_secret_key
        ),
        "vapid_public_key": request.app.state.vapid_public_key,
    }


@router.post("/subscriptions", status_code=201)
async def subscribe(payload: PushSubscriptionInput, request: Request):
    client = notification_client(request)
    row = {
        "user_id": request.state.user_id,
        "endpoint": str(payload.endpoint),
        "p256dh": payload.keys.p256dh,
        "auth": payload.keys.auth,
        "timezone": payload.timezone,
        "language": payload.language,
        "disabled_at": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    client.table("push_subscriptions").upsert(row, on_conflict="endpoint").execute()
    return {"subscribed": True}


@router.delete("/subscriptions")
async def unsubscribe(payload: PushSubscriptionDelete, request: Request):
    notification_client(request).table("push_subscriptions").delete().eq(
        "endpoint", str(payload.endpoint)
    ).eq("user_id", request.state.user_id).execute()
    return {"subscribed": False}
