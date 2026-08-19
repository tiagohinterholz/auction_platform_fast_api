import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Logs one line per request: method, path, status, duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            duration = time.monotonic() - start_time
            logger.exception(
                f"Method: {request.method} | "
                f"Path: {request.url.path} | "
                f"Status: 500 (unhandled) | "
                f"Duration: {duration:.2f}s"
            )
            raise

        duration = time.monotonic() - start_time
        log_message = (
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.2f}s"
        )

        if response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response


class RequestIDLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True
