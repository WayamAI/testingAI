import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest_docs import build_docx_bytes


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_doc_driven_generates_real_tests_without_a_connected_repo():
    """Doc-driven generation works even for a project that was never
    connected to a repo — it only needs the document."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "docdriven@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Doc Driven Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        docx_bytes = build_docx_bytes([
            "Users should be able to log in with a valid email and password.",
            "The system must allow users to add items to their shopping cart.",
            "This is just background context with no testable requirement.",
        ])
        files = {"file": ("prd.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        upload_resp = await client.post(f"/api/testing/doc-driven/{project['id']}/upload", files=files, headers=headers)

        assert upload_resp.status_code == 200
        body = upload_resp.json()
        assert body["scenarios_extracted"] >= 2
        assert body["tests_generated"] >= 2
        assert body["rejected_invalid_syntax"] == 0
        for t in body["tests"]:
            assert "require('@playwright/test')" in t["code"]
            assert t["file_path"] is None  # no connected workspace to write into

        uploads_resp = await client.get(f"/api/testing/doc-driven/{project['id']}/uploads", headers=headers)
        uploads = uploads_resp.json()
        assert len(uploads) == 1
        assert uploads[0]["filename"] == "prd.docx"


@pytest.mark.asyncio
async def test_doc_driven_rejects_unsupported_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "docdrivenbad@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Bad Upload Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        files = {"file": ("archive.zip", b"PK\x03\x04", "application/zip")}
        upload_resp = await client.post(f"/api/testing/doc-driven/{project['id']}/upload", files=files, headers=headers)
        assert upload_resp.status_code == 422
        assert "Unsupported file type" in upload_resp.json()["detail"]
