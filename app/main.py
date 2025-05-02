from fastapi import FastAPI, Request
from .middleware.rate_limiter import RateLimiterMiddleware

app = FastAPI()
app.add_middleware(RateLimiterMiddleware)


@app.get("/test/path")
async def test_endpoint():
    return {"message": "allowed"}
