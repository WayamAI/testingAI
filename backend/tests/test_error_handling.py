import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.middleware.error_handler import install_error_handlers


@pytest.mark.asyncio
async def test_unhandled_exception_returns_safe_json_shape():
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/boom")
    async def boom():
        raise RuntimeError("db connection string leaked: mongodb://user:pass@host")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/boom")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "internal_error"
    assert "mongodb://" not in body["error"]["message"]
