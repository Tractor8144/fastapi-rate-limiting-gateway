from fastapi import FastAPI, Request
from .middleware.rate_limiter import RateLimiterMiddleware
from starlette.responses import Response
import httpx

app = FastAPI()
app.add_middleware(RateLimiterMiddleware)

BACKEND_URL = 'http://localhost:9000'


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    req_body = await request.body()
    headers = dict(request.headers)

    async with httpx.AsyncClient() as client:
        backend_response = await client.request(
            method=request.method,
            url=f"{BACKEND_URL}/{full_path}",
            headers=headers,
            content=req_body,
            params=request.query_params
        )

    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers),
        media_type=backend_response.headers.get("content-type")
    )
