import os
import structlog
import uuid
from starlette.responses import Response
from fastapi import Request

_logger = None


def configure_logging() -> None:
    global _logger
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    )
    _logger = structlog.get_logger()


def get_logger():
    global _logger
    if _logger is None:
        configure_logging()
    return _logger


async def with_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response