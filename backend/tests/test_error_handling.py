import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, HTTPException
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


@pytest.mark.asyncio
async def test_http_exception_preserves_status_code_and_detail():
    """Verify that HTTPException is not caught by the generic exception handler.

    This ensures that 404s, 401s, and other HTTP-specific exceptions still
    return their proper status codes and detail messages, not converted to
    generic 500 internal_error responses.
    """
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/not-found")
    async def not_found():
        raise HTTPException(status_code=404, detail="Project not found")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/not-found")

    # Verify the response is 404, not 500
    assert resp.status_code == 404
    # Verify the detail is preserved, not replaced with generic internal_error message
    body = resp.json()
    assert body["detail"] == "Project not found"
