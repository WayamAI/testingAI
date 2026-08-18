import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _auth_client(client):
    login = await client.post("/api/auth/login", json={"email": "crud@example.com", "password": "x"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_requirement_suite_case_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_client(client)

        proj = await client.post(
            "/api/projects", json={"name": "Flow Project", "project_type": "web_application"}, headers=headers
        )
        project_id = proj.json()["id"]

        req = await client.post(
            "/api/requirements",
            json={"project_id": project_id, "title": "Password reset", "description": "Users reset via email"},
            headers=headers,
        )
        assert req.status_code == 201
        requirement_id = req.json()["id"]

        case = await client.post(
            "/api/test-cases",
            json={
                "project_id": project_id,
                "requirement_id": requirement_id,
                "title": "Reset happy path",
                "type": "functional",
                "priority": "high",
                "steps": ["Go to reset page", "Submit valid email"],
                "expected_result": "Email sent",
            },
            headers=headers,
        )
        assert case.status_code == 201
        case_id = case.json()["id"]

        suite = await client.post(
            "/api/test-suites",
            json={"project_id": project_id, "name": "Auth Suite"},
            headers=headers,
        )
        assert suite.status_code == 201
        suite_id = suite.json()["id"]

        add = await client.post(
            f"/api/test-suites/{suite_id}/add-cases",
            json={"case_ids": [case_id]},
            headers=headers,
        )
        assert add.status_code == 200
        assert case_id in add.json()["test_case_ids"]
