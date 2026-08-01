import logging

from fastapi import HTTPException

from ..llm.graph import ConfigurationError

logger = logging.getLogger(__name__)


async def service_call(awaitable):
    try:
        return await awaitable
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Board operation failed")
        raise HTTPException(status_code=502, detail="The assistant could not process this request") from exc
