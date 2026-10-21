import logging
import time
from urllib import response

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.metrics import record_request
from app.core.request_context import (
    generate_request_id,
    set_request_id,
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = request.headers.get(
            "X-Request-ID"
        ) or generate_request_id()

        set_request_id(request_id)

        start_time = time.perf_counter()

        logger.info(
            "Request started | request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000
            record_request(
            path=request.url.path,
            duration_ms=duration_ms,
            )
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "Request completed | request_id=%s | "
                "status=%s | duration_ms=%.2f",
                request_id,
                response.status_code,
                duration_ms,
            )

            return response

        except Exception:
            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.exception(
                "Request failed | request_id=%s | "
                "duration_ms=%.2f",
                request_id,
                duration_ms,
            )

            raise

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import record_request
from app.core.request_context import (
    generate_request_id,
    set_request_id,
)


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = request.headers.get(
            "X-Request-ID"
        ) or generate_request_id()

        set_request_id(request_id)

        start_time = time.perf_counter()

        logger.info(
            "Request started | request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            record_request(
                path=request.url.path,
                duration_ms=duration_ms,
            )

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "Request completed | request_id=%s | "
                "status=%s | duration_ms=%.2f",
                request_id,
                response.status_code,
                duration_ms,
            )

            return response

        except Exception:
            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.exception(
                "Request failed | request_id=%s | "
                "duration_ms=%.2f",
                request_id,
                duration_ms,
            )

            raise