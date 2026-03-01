"""Basic rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import get_logger

logger = get_logger(__name__)

_MAX_REQUESTS_PER_MINUTE = 10
_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-IP rate limiter."""

    def __init__(self, app: Callable) -> None:
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before forwarding the request."""
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Prune old entries
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if now - ts < _WINDOW_SECONDS
        ]

        if len(self._requests[client_ip]) >= _MAX_REQUESTS_PER_MINUTE:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return Response(
                content='{"detail":"Rate limit exceeded. Try again shortly."}',
                status_code=429,
                media_type="application/json",
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
