import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _setup_project_with_results(client):
    login = await client.post("/api/auth/login", json={"email": "quser@example.com", "password": "x"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    proj = await client.post("/api/projects", json={"name": "Quality Project", "project_type": "web_application"}, headers=headers)
    project_id = proj.json()["id"]
    suite = await client.post("/api/test-suites", json={"project_id": project_id, "name": "Suite"}, headers=headers)
    suite_id = suite.json()["id"]
    run = await client.post("/api/test-runs", json={"suite_id": suite_id}, headers=headers)
    return headers, project_id, run.json()["id"]


@pytest.mark.asyncio
async def test_defect_creation_and_release_readiness_blocks_on_critical():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers, project_id, run_id = await _setup_project_with_results(client)

        defect = await client.post(
            "/api/defects",
            json={
                "project_id": project_id,
                "title": "Payment timeout under load",
                "description": "Checkout times out for large carts",
                "severity": "critical",
                "priority": "high",
            },
            headers=headers,
        )
        assert defect.status_code == 201

        readiness = await client.get(f"/api/quality/release-readiness?project_id={project_id}", headers=headers)
        assert readiness.status_code == 200
        body = readiness.json()
        assert body["status"] == "BLOCKED"
        assert body["critical_defects"] >= 1
        assert "critical defect" in " ".join(body["gate_violations"]).lower()
