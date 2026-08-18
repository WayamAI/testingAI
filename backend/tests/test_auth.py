import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_demo_login_returns_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/auth/demo-login")
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"]


@pytest.mark.asyncio
async def test_demo_mode_accepts_any_credentials():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/login",
            json={"email": "newclient@example.com", "password": "anything123"},
        )
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "newclient@example.com"


@pytest.mark.asyncio
async def test_protected_route_rejects_missing_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/projects")
    assert resp.status_code == 401
