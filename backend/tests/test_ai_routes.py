import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_generate_tests_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/auth/login", json={"email": "aiuser@example.com", "password": "x"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        resp = await client.post(
            "/api/ai/generate-tests",
            json={"requirement_text": "Users can reset their password using their registered email."},
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["source"] in ("ai", "demo_fallback")
        assert len(body["cases"]) >= 5


@pytest.mark.asyncio
async def test_analyze_failure_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/auth/login", json={"email": "aiuser2@example.com", "password": "x"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        resp = await client.post(
            "/api/ai/analyze-failure",
            json={
                "error_message": "Timeout waiting for element #submit-payment",
                "stack_trace": "TimeoutError at checkout.spec.ts:42",
                "test_case_title": "Checkout: submit payment",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["analysis"]["root_cause"]
        assert body["source"] in ("ai", "demo_fallback")
