from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import HOUSEHOLD_COOKIE, authenticate, data_client, router as auth_router, set_auth_cookies
from board_api import router as board_router
from conversation_api import router as conversation_router
from weather import WeatherService

load_dotenv()
ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.supabase_url = os.getenv("SUPABASE_URL", "")
    app.state.supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    app.state.public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
    if not app.state.supabase_url or not app.state.supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are required")
    app.state.weather = WeatherService(os.getenv("OPENWEATHER_API_KEY"))
    yield


app = FastAPI(title="Hearthbook", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(auth_router)
app.include_router(board_router)
app.include_router(conversation_router)


@app.middleware("http")
async def require_session(request: Request, call_next):
    path = request.url.path
    if not path.startswith("/api/") or path.startswith("/api/auth/"):
        return await call_next(request)
    authenticated = authenticate(request)
    if authenticated is None:
        return JSONResponse({"detail": "Authentication required"}, status_code=401)
    user, access_token, refreshed = authenticated
    request.state.user_id = str(user.id)
    request.state.access_token = access_token
    client = data_client(request, access_token)
    request.state.data_client = client
    memberships = client.table("household_memberships").select("household_id").eq("user_id", str(user.id)).execute().data or []
    household_ids = [row["household_id"] for row in memberships]
    requested = request.cookies.get(HOUSEHOLD_COOKIE)
    request.state.household_id = requested if requested in household_ids else household_ids[0] if household_ids else None
    if request.state.household_id is None and path not in {"/api/households", "/api/households/join"}:
        return JSONResponse({"detail": "Household setup required"}, status_code=409)
    try:
        response = await call_next(request)
    finally:
        database = getattr(request.state, "database", None)
        if database:
            database.close()
    if refreshed:
        set_auth_cookies(response, refreshed, request)
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: https://openweathermap.org; "
        "script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=(self)"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https" or request.app.state.public_domain:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


def main():
    port = os.getenv("PORT")
    uvicorn.run("app:app", host="0.0.0.0" if port else "127.0.0.1", port=int(port or 8000), reload=not port)


if __name__ == "__main__":
    main()
