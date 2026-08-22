import io
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
async def test_security_scan_route_flags_real_vulnerable_dependency():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "secscan@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Vulnerable Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        zip_bytes = _zip_directory(FIXTURES / "vulnerable_python_project")
        files = {"file": ("fixture.zip", zip_bytes, "application/zip")}
        await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)

        scan_resp = await client.post(f"/api/projects/{project['id']}/security-scans", headers=headers)
        assert scan_resp.status_code == 200
        summary = scan_resp.json()
        assert summary["total_findings"] > 0
        assert "ran" in summary["provider_status"]["pip-audit"]

        findings_resp = await client.get(f"/api/projects/{project['id']}/security-findings", headers=headers)
        findings = findings_resp.json()
        assert any(f["tool"] == "pip-audit" for f in findings)


@pytest.mark.asyncio
async def test_security_scan_route_rejects_unconnected_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "secscanunconnected@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Never Connected", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        scan_resp = await client.post(f"/api/projects/{project['id']}/security-scans", headers=headers)
        assert scan_resp.status_code == 422


@pytest.mark.asyncio
async def test_api_testing_route_reports_missing_spec_when_none_connected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "apitestnospec@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "No Spec Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        zip_bytes = _zip_directory(FIXTURES / "jest_project")
        files = {"file": ("fixture.zip", zip_bytes, "application/zip")}
        await client.post(f"/api/projects/{project['id']}/connect-zip", files=files, headers=headers)

        run_resp = await client.post(
            f"/api/projects/{project['id']}/api-tests", json={"base_url": "http://127.0.0.1:9999"}, headers=headers
        )
        assert run_resp.status_code == 422
        assert "No OpenAPI/Swagger spec found" in run_resp.json()["detail"]
