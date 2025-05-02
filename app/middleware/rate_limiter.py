from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import random  # remove later


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> JSONResponse:
        choices_allowed = (True, False)
        allowed = random.choices(choices_allowed)
        if not allowed[0]:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Too many requests'}
            )

        response = await call_next(request)
        return response
