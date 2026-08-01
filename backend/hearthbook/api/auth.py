from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from supabase import Client, create_client
from supabase_auth.errors import AuthError

ACCESS_COOKIE = "hearthbook_access"
REFRESH_COOKIE = "hearthbook_refresh"
HOUSEHOLD_COOKIE = "hearthbook_household"
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class AuthInput(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class HouseholdInput(BaseModel):
    household_name: str = Field(min_length=1, max_length=80)
    member_name: str = Field(min_length=1, max_length=40)


class JoinInput(BaseModel):
    invite_code: str = Field(min_length=1, max_length=40)
    member_name: str = Field(min_length=1, max_length=40)
    member_role: str = Field(default="", max_length=40)


class SelectInput(BaseModel):
    household_id: str = Field(min_length=1, max_length=80)


def auth_client(request: Request) -> Client:
    return create_client(request.app.state.supabase_url, request.app.state.supabase_key)


def data_client(request: Request, access_token: str) -> Client:
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


def secure_request(request: Request) -> bool:
    return request.url.scheme == "https" or bool(request.app.state.public_domain)


def set_auth_cookies(response: Response, session, request: Request) -> None:
    secure = secure_request(request)
    response.set_cookie(ACCESS_COOKIE, session.access_token, max_age=session.expires_in, httponly=True, secure=secure, samesite="lax")
    response.set_cookie(REFRESH_COOKIE, session.refresh_token, max_age=30 * 24 * 60 * 60, httponly=True, secure=secure, samesite="lax")


def set_household_cookie(response: Response, household_id: str, request: Request) -> None:
    response.set_cookie(HOUSEHOLD_COOKIE, household_id, max_age=365 * 24 * 60 * 60, httponly=True, secure=secure_request(request), samesite="lax")


@router.post("/auth/signup")
async def signup(payload: AuthInput, request: Request, response: Response):
    try:
        result = auth_client(request).auth.sign_up({"email": payload.email.strip(), "password": payload.password})
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result.session:
        set_auth_cookies(response, result.session, request)
    return {"authenticated": result.session is not None, "confirmation_required": result.session is None}


@router.post("/auth/login")
async def login(payload: AuthInput, request: Request, response: Response):
    try:
        result = auth_client(request).auth.sign_in_with_password({"email": payload.email.strip(), "password": payload.password})
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="Invalid email or password") from exc
    if not result.session:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    set_auth_cookies(response, result.session, request)
    return {"authenticated": True}


@router.get("/auth/session")
async def session(request: Request, response: Response):
    authenticated = authenticate(request)
    if authenticated is None:
        return {"authenticated": False, "household_ready": False}
    user, access_token, refreshed = authenticated
    if refreshed:
        set_auth_cookies(response, refreshed, request)
    client = data_client(request, access_token)
    memberships = client.table("household_memberships").select("household_id").eq("user_id", str(user.id)).execute().data or []
    household_ids = [row["household_id"] for row in memberships]
    households = client.table("households").select("id,name").in_("id", household_ids).execute().data or [] if household_ids else []
    requested = request.cookies.get(HOUSEHOLD_COOKIE)
    active = requested if requested in household_ids else household_ids[0] if household_ids else None
    if active and active != requested:
        set_household_cookie(response, active, request)
    return {
        "authenticated": True,
        "email": user.email,
        "household_ready": bool(households),
        "households": households,
        "active_household_id": active,
    }


@router.delete("/auth/session")
async def logout(response: Response):
    for cookie in (ACCESS_COOKIE, REFRESH_COOKIE, HOUSEHOLD_COOKIE):
        response.delete_cookie(cookie, httponly=True, samesite="lax")
    return {"authenticated": False}


def safe_household_error(exc: Exception) -> str:
    error = str(exc)
    for message in ("Invalid household or member name", "Invalid household invite", "Invalid member name", "Invalid member name or role", "This account already belongs to this household"):
        if message in error:
            return message
    logger.exception("Household operation failed")
    return "Could not update household"


@router.post("/households", status_code=201)
async def create_household(payload: HouseholdInput, request: Request, response: Response):
    try:
        result = data_client(request, request.state.access_token).rpc(
            "create_household", {"household_name": payload.household_name, "member_name": payload.member_name}
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=safe_household_error(exc)) from exc
    set_household_cookie(response, result.data, request)
    return {"created": True, "household_id": result.data}


@router.post("/households/join")
async def join_household(payload: JoinInput, request: Request, response: Response):
    try:
        result = data_client(request, request.state.access_token).rpc(
            "join_household", {
                "household_invite_code": payload.invite_code,
                "member_name": payload.member_name,
                "member_role": payload.member_role,
            }
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=safe_household_error(exc)) from exc
    set_household_cookie(response, result.data, request)
    return {"joined": True, "household_id": result.data}


@router.post("/households/select")
async def select_household(payload: SelectInput, request: Request, response: Response):
    membership = data_client(request, request.state.access_token).table("household_memberships").select("household_id").eq("user_id", request.state.user_id).eq("household_id", payload.household_id).maybe_single().execute()
    if membership is None or membership.data is None:
        raise HTTPException(status_code=404, detail="Household not found")
    set_household_cookie(response, payload.household_id, request)
    return {"selected": True}
