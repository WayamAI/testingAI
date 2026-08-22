import shutil

import pytest
from httpx import ASGITransport, AsyncClient

from app.intake.workspace import workspace_path
from app.main import app
from app.services import git_mining
from tests.conftest_git import build_risky_repo


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_root_cause_correlates_with_real_commit_touching_the_stack_trace_file(tmp_path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "rootcause@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Root Cause Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        repo = build_risky_repo(tmp_path)
        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo, target)

        commits = await git_mining.get_recent_commits(target, limit=10)
        most_recent_risky_commit = commits[0]  # "feat: extend risky with extra helper" — newest, touches risky.js

        resp = await client.post(
            f"/api/testing/root-cause/{project['id']}/analyze",
            json={
                "error_message": "AssertionError: expected 4 but got 3",
                "stack_trace": "at Object.<anonymous> (src/risky.js:2:10)",
                "test_case_title": "risky calculation test",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["git_correlation_available"] is True
        assert body["likely_commit_sha"] == most_recent_risky_commit.sha
        assert body["likely_commit_message"] == most_recent_risky_commit.message
        assert body["source"] in ("ai", "demo_fallback")

        history_resp = await client.get(f"/api/testing/root-cause/{project['id']}/history", headers=headers)
        history = history_resp.json()
        assert len(history) == 1
        assert history[0]["likely_commit_sha"] == most_recent_risky_commit.sha

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_root_cause_without_connected_workspace_still_returns_a_real_analysis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "rootcausenogit@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "No Git Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        resp = await client.post(
            f"/api/testing/root-cause/{project['id']}/analyze",
            json={
                "error_message": "Timeout waiting for element #submit",
                "stack_trace": "TimeoutError at checkout.spec.ts:12",
                "test_case_title": "checkout flow",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["git_correlation_available"] is False
        assert body["likely_commit_sha"] is None
        assert body["root_cause"]
