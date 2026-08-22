import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_dashboard_returns_aggregate_metrics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/auth/login", json={"email": "dash@example.com", "password": "x"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        proj = await client.post("/api/projects", json={"name": "Dash Project", "project_type": "web_application"}, headers=headers)
        project_id = proj.json()["id"]

        resp = await client.get(f"/api/dashboard?project_id={project_id}", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        for key in ("total_tests", "executed", "passed", "failed", "pass_rate", "quality_score", "recent_runs"):
            assert key in body
