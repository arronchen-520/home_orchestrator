from fastapi import HTTPException, Request

from ..services.board import BoardService
from ..storage.board import BoardDatabase
from .auth import data_client


def board_service(request: Request) -> BoardService:
    service = getattr(request.state, "board_service", None)
    if service is None:
        database = BoardDatabase(
            getattr(request.state, "data_client", None)
            or data_client(request, request.state.access_token)
        )
        request.state.database = database
        member_id = database.require_user_member(
            request.state.household_id, request.state.user_id
        )
        request.state.member_id = member_id
        service = BoardService(database, request.state.household_id, member_id)
        request.state.board_service = service
    return service


def consume_ai_quota(request: Request) -> None:
    database = getattr(request.state, "database", None)
    if database is None:
        database = BoardDatabase(
            getattr(request.state, "data_client", None)
            or data_client(request, request.state.access_token)
        )
        request.state.database = database
    quota = database.consume_ai_quota(request.state.household_id)
    if not quota.get("allowed"):
        raise HTTPException(status_code=429, detail={"code": "daily_ai_limit"})
