from fastapi import Request

from auth import data_client
from board_db import BoardDatabase
from board_service import BoardService


def board_service(request: Request) -> BoardService:
    service = getattr(request.state, "board_service", None)
    if service is None:
        database = BoardDatabase(
            getattr(request.state, "data_client", None)
            or data_client(request, request.state.access_token)
        )
        request.state.database = database
        service = BoardService(database, request.state.household_id)
        request.state.board_service = service
    return service
