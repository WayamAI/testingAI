import shutil
import threading
import time

import pytest
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from httpx import ASGITransport, AsyncClient
import uvicorn

from app.intake.workspace import workspace_path
from app.main import app

_HTML = """
<!doctype html><html><body>
  <button id="submit-payment-btn">Submit Payment</button>
  <a href="/help">Help</a>
</body></html>
"""


@pytest.fixture(scope="module")
def live_target_server():
    target_app = FastAPI()

    @target_app.get("/", response_class=HTMLResponse)
    async def index():
        return _HTML

    config = uvicorn.Config(target_app, host="127.0.0.1", port=8767, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    yield "http://127.0.0.1:8767"
    server.should_exit = True
    thread.join(timeout=5)


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_propose_heals_to_a_real_live_dom_candidate(live_target_server):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "selfheal@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Self Heal Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        resp = await client.post(
            f"/api/testing/self-heal/{project['id']}/propose",
            json={
                "url": live_target_server,
                "original_selector": "#submit-payment",
                "failure_context": "TimeoutError: locator('#submit-payment') not found",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()

        # Real element on the real page — never a fabricated selector.
        assert body["proposed_selector"] == "#submit-payment-btn"
        assert body["live_validation_count"] == 1
        assert body["status"] == "proposed"
        assert body["source"] in ("ai", "demo_fallback")

        list_resp = await client.get(f"/api/testing/self-heal/{project['id']}/attempts", headers=headers)
        assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_approve_writes_back_to_a_real_file_only_after_approval(live_target_server, tmp_path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "selfhealapprove@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Self Heal Approve Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        spec_file = target / "checkout.spec.js"
        spec_file.write_text(
            "const { test, expect } = require('@playwright/test');\n"
            "test('checkout', async ({ page }) => {\n"
            "  await page.click('#submit-payment');\n"
            "});\n"
        )

        propose_resp = await client.post(
            f"/api/testing/self-heal/{project['id']}/propose",
            json={"url": live_target_server, "original_selector": "#submit-payment", "failure_context": "not found"},
            headers=headers,
        )
        attempt_id = propose_resp.json()["id"]

        # Write-back must not happen before approval.
        assert "#submit-payment'" in spec_file.read_text()

        approve_resp = await client.post(
            f"/api/testing/self-heal/{project['id']}/attempts/{attempt_id}/approve",
            json={"target_file": "checkout.spec.js", "target_line": 3},
            headers=headers,
        )
        assert approve_resp.status_code == 200
        approved = approve_resp.json()
        assert approved["status"] == "approved"
        assert approved["applied"] is True

        updated_content = spec_file.read_text()
        assert "#submit-payment-btn" in updated_content
        assert "#submit-payment'" not in updated_content

        # A second approval attempt is rejected — already approved.
        second_approve = await client.post(
            f"/api/testing/self-heal/{project['id']}/attempts/{attempt_id}/approve",
            json={},
            headers=headers,
        )
        assert second_approve.status_code == 422

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_propose_reports_no_candidates_on_a_dead_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "selfhealdead@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Dead URL Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        resp = await client.post(
            f"/api/testing/self-heal/{project['id']}/propose",
            json={"url": "http://127.0.0.1:9999/nope", "original_selector": "#x", "failure_context": "not found"},
            headers=headers,
        )
        assert resp.status_code == 422
