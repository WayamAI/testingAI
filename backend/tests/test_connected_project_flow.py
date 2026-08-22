import io
import shutil
import zipfile
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

FIXTURES = Path(__file__).parent / "fixtures"


def _zip_directory(source: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for file in source.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(source))
    return buf.getvalue()


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_connect_zip_detects_real_stack_and_updates_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "connectzip@example.com")

        create_resp = await client.post(
            "/api/projects", json={"name": "Connected Jest Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        zip_bytes = _zip_directory(FIXTURES / "jest_project")
        files = {"file": ("fixture.zip", zip_bytes, "application/zip")}
        connect_resp = await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)

        assert connect_resp.status_code == 200
        body = connect_resp.json()
        assert body["source"] == "connected"
        assert body["intake_status"] == "ready"
        assert body["detected_language"] == "javascript/typescript"
        assert body["detected_test_framework"] == "jest"


@pytest.mark.asyncio
async def test_connect_zip_reports_reason_when_no_manifest_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "connectnomanifest@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "No Manifest Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        zip_bytes = _zip_directory(FIXTURES / "no_manifest_project")
        files = {"file": ("fixture.zip", zip_bytes, "application/zip")}
        connect_resp = await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)

        assert connect_resp.status_code == 200
        body = connect_resp.json()
        assert body["source"] == "connected"
        assert body["detected_language"] is None
        assert "No recognized test manifest" in body["intake_error"]


@pytest.mark.asyncio
async def test_connect_zip_rejects_path_traversal_archive():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "connecttraversal@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Traversal Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../../evil.txt", "pwned")
        files = {"file": ("evil.zip", buf.getvalue(), "application/zip")}
        connect_resp = await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)

        assert connect_resp.status_code == 422


@pytest.mark.asyncio
async def test_full_connected_run_produces_real_results_over_websocket():
    """End-to-end: connect a real fixture, create a suite/run, and drive
    execute_and_persist directly (WebSocket transport isn't exercised by
    httpx's ASGI transport) to verify genuine pass/fail persistence."""
    from app.services import execution_service, testing_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "fullrun@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Full Run Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        zip_bytes = _zip_directory(FIXTURES / "jest_project")
        files = {"file": ("fixture.zip", zip_bytes, "application/zip")}
        connect_resp = await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)
        assert connect_resp.status_code == 200

    suite = await testing_service.create_test_suite(
        project["organization_id"], "system", project["id"], "Detected Tests", ""
    )
    run = await execution_service.create_run(project["organization_id"], "system", project["id"], suite.id)

    events = []

    async def on_event(event):
        events.append(event)

    await execution_service.execute_and_persist(project["organization_id"], project["id"], run, [], on_event)

    result_events = [e for e in events if e.type == "result"]
    assert len(result_events) == 3
    statuses = {e.status for e in result_events}
    assert "passed" in statuses
    assert "failed" in statuses

    final_run = await execution_service.get_run(project["organization_id"], run.id)
    assert final_run.status == "completed"
    assert final_run.passed == 2
    assert final_run.failed == 1
