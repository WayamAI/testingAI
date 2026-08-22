import shutil

import pytest
from httpx import ASGITransport, AsyncClient

from app.intake.workspace import workspace_path
from app.main import app
from tests.conftest_git import build_risky_repo


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_full_baseline_scan_generates_real_syntactically_valid_tests(tmp_path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "baseline@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Baseline Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        repo = build_risky_repo(tmp_path)
        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo, target)

        scan_resp = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        assert scan_resp.status_code == 200
        body = scan_resp.json()

        # Demo fallback always succeeds (no OLLAMA_API_KEY in test env) and
        # produces one test per requested category — first scan requests all 10.
        assert body["source"] in ("ai", "demo_fallback")
        assert body["generated"] == 10
        assert body["rejected_invalid_syntax"] == 0
        assert set(body["categories_scanned"]) >= {"auth", "api", "performance", "accessibility"}

        list_resp = await client.get(f"/api/testing/baseline/{project['id']}/tests", headers=headers)
        tests = list_resp.json()
        assert len(tests) == 10
        # Every persisted test's code is real, non-empty Playwright JS.
        for t in tests:
            assert "require('@playwright/test')" in t["code"]
            assert t["file_path"].endswith(".spec.js")

        # Second scan with no commits since: reports nothing new, doesn't duplicate.
        rescan_resp = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        rescan_body = rescan_resp.json()
        assert rescan_body["generated"] == 0
        assert "No new commits" in rescan_body["message"]

        list_after = await client.get(f"/api/testing/baseline/{project['id']}/tests", headers=headers)
        assert len(list_after.json()) == 10  # unchanged, not duplicated

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_incremental_rescan_appends_only_for_changed_categories(tmp_path):
    import subprocess

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "incremental@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Incremental Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        repo = build_risky_repo(tmp_path)
        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo, target)

        first = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        assert first.json()["generated"] == 10

        # A real new commit touching a file that maps to the "auth" category.
        (target / "src" / "auth_login.js").write_text("export function login() { return true; }\n")
        subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "feat: add login"], cwd=target, check=True, capture_output=True)

        second = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        second_body = second.json()
        assert second_body["generated"] >= 1
        assert "auth" in second_body["categories_scanned"]

        list_resp = await client.get(f"/api/testing/baseline/{project['id']}/tests", headers=headers)
        # Original 10 plus the newly appended one(s) — never fewer, never duplicated wholesale.
        assert len(list_resp.json()) == 10 + second_body["generated"]

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_baseline_scan_rejects_unconnected_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "baselineunconnected@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Never Connected Baseline", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        scan_resp = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        assert scan_resp.status_code == 422
