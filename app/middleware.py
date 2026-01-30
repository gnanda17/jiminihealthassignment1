"""Request logging middleware with PHI redaction."""

import logging
import re
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Query params that contain PHI and must be redacted
PHI_QUERY_PARAMS = {"patientId", "patientid", "patient_id"}


def redact_query_params(query_string: str) -> str:
    """Redact PHI query parameters from query string."""
    if not query_string:
        return query_string

    def redact_match(match: re.Match) -> str:
        key = match.group(1)
        if key.lower().replace("_", "") in {"patientid"}:
            return f"{key}=[REDACTED]"
        return match.group(0)

    return re.sub(r"([^&=]+)=([^&]*)", redact_match, query_string)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs requests with PHI redaction."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        redacted_query = redact_query_params(str(request.query_params))
        query_part = f"?{redacted_query}" if redacted_query else ""

        logger.info("Request: %s %s%s", request.method, request.url.path, query_part)

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        logger.info(
            "Response: %s %s status=%d duration=%.3fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response
