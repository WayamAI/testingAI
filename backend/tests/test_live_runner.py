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
<!doctype html><html><head><title>Fixture App</title></head><body>
  <input type="email" name="email" placeholder="Email" />
  <input type="password" name="password" placeholder="Password" />
  <button type="submit">Log In</button>
  <a href="/about">About</a>
</body></html>
"""


@pytest.fixture(scope="module")
def live_target_server():
    target_app = FastAPI()

    @target_app.get("/", response_class=HTMLResponse)
    async def index():
        return _HTML

    config = uvicorn.Config(target_app, host="127.0.0.1", port=8768, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    yield "http://127.0.0.1:8768"
    server.should_exit = True
    thread.join(timeout=5)


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_live_runner_executes_real_tests_with_real_screenshots(live_target_server):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "liverunner@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Live Runner Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        run_resp = await client.post(
            f"/api/testing/live-runner/{project['id']}/run", json={"url": live_target_server}, headers=headers
        )
        assert run_resp.status_code == 200
        body = run_resp.json()

        # A login-shaped page should trigger auth + ui_form categories in
        # addition to the always-included ui_component baseline.
        assert "auth" in body["categories"]
        assert "ui_form" in body["categories"]
        assert body["total"] > 0
        assert body["passed"] + body["failed"] == body["total"]
        assert body["source"] in ("ai", "demo_fallback")

        for r in body["results"]:
            assert r["status"] in ("passed", "failed", "timedOut", "interrupted")
            if r["screenshot_path"]:
                from pathlib import Path
                assert Path(r["screenshot_path"]).exists()  # a genuine screenshot file on disk

        runs_resp = await client.get(f"/api/testing/live-runner/{project['id']}/runs", headers=headers)
        runs = runs_resp.json()
        assert len(runs) == 1
        assert runs[0]["id"] == body["run_id"]

    shutil.rmtree(workspace_path(project["id"]), ignore_errors=True)


@pytest.mark.asyncio
async def test_live_runner_reports_error_for_unreachable_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "liverunnerdead@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Dead Live Runner Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        run_resp = await client.post(
            f"/api/testing/live-runner/{project['id']}/run",
            json={"url": "http://127.0.0.1:9999/nope"}, headers=headers,
        )
        assert run_resp.status_code == 422
