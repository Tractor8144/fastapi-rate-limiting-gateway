import pytest
from httpx import AsyncClient
from app.main import app
from httpx._transports.asgi import ASGITransport


@pytest.mark.asyncio
async def test_health_check_proxy():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resonse = await ac.get("/health")
    assert resonse.status_code == 200
    assert resonse.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_rate_limiting_blocks_after_limit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for i in range(5):
            res = await ac.get('/health')
            assert res.status_code == 200, f"Failed om request {i+1}"

        res = await ac.get('/health')
        assert res.status_code == 429
        assert res.json() == {'detail': 'Too many requests'}
