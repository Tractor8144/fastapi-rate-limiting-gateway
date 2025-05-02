from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.services.redis_handler import get_token_bucket


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> JSONResponse:
        key = f"rate_limit:{request.client.host}"
        allowed = get_token_bucket(key, limit=5, refill_rate=1)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Too many requests'}
            )

        response = await call_next(request)
        return response
