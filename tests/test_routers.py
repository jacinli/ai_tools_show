from fastapi.testclient import TestClient
from routers.sse_router import app
import pytest
from httpx import AsyncClient,ASGITransport

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"msg": "pong"}



@pytest.mark.asyncio
async def test_hello():
    # ✅ 推荐使用 transport 显式传入 app，避免 DeprecationWarning & 502 错误
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello async!"}