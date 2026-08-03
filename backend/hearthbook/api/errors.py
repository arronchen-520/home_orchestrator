import logging

from fastapi import HTTPException, Request

from ..llm.graph import ConfigurationError

logger = logging.getLogger(__name__)


def request_context(request: Request | None) -> str:
    if request is None:
        return "path=unknown household_id=unknown session_id=unknown user_id=unknown"
    state = request.state
    return (
        f"path={request.url.path} household_id={getattr(state, 'household_id', None)} "
        f"session_id={getattr(state, 'session_id', None)} user_id={getattr(state, 'user_id', None)}"
    )


async def service_call(awaitable, request: Request | None = None, operation: str = "assistant"):
    try:
        return await awaitable
    except ConfigurationError as exc:
        logger.error(
            "Service configuration error operation=%s error=%s %s",
            operation,
            exc,
            request_context(request),
        )
        raise HTTPException(status_code=503, detail={"code": "service_unavailable"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Service operation failed operation=%s error_type=%s %s",
            operation,
            type(exc).__name__,
            request_context(request),
        )
        raise HTTPException(status_code=502, detail={"code": "assistant_unavailable"}) from exc
