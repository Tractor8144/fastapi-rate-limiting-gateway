from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.services.redis_handler import get_token_bucket
from app.services.status_enum import StatusType

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> JSONResponse:
        key = f"rate_limit:{request.client.host}"
        status = get_token_bucket(key, limit=5, refill_rate=1)
        if status==StatusType.REFUSED:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Too many requests'}
            )
        elif status==StatusType.REDIS_ERROR:
            return JSONResponse(
                status_code=503,
                content={'detail':'Redis server error'}
            )
        response = await call_next(request)
        return response
