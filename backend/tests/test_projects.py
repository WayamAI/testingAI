import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _login(client, email):
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_and_list_projects():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, "org1user@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = await client.post(
            "/api/projects",
            json={"name": "Acme Commerce", "project_type": "e_commerce"},
            headers=headers,
        )
        assert create_resp.status_code == 201

        list_resp = await client.get("/api/projects", headers=headers)
        assert list_resp.status_code == 200
        names = [p["name"] for p in list_resp.json()]
        assert "Acme Commerce" in names


@pytest.mark.asyncio
async def test_projects_isolated_by_organization():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token_a = await _login(client, "orga@example.com")
        token_b = await _login(client, "orgb@example.com")

        await client.post(
            "/api/projects",
            json={"name": "Org A Project", "project_type": "web_application"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        list_b = await client.get("/api/projects", headers={"Authorization": f"Bearer {token_b}"})
        names = [p["name"] for p in list_b.json()]
        assert "Org A Project" not in names
