import shutil
import subprocess

import pytest
from httpx import ASGITransport, AsyncClient

from app.database.mongo import get_database
from app.intake.workspace import workspace_path
from app.main import app
from app.models.base import new_id
from app.models.test_case import TestCase
from app.models.test_result import TestResult
from tests.conftest_git import build_risky_repo


async def _login_and_headers(client: AsyncClient, email: str) -> dict:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "x"})
    body = resp.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["organization_id"]


@pytest.mark.asyncio
async def test_selection_prioritizes_tests_matching_real_changed_files(tmp_path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers, org_id = await _login_and_headers(client, "selection@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Selection Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        repo = build_risky_repo(tmp_path)
        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo, target)

        first_scan = await client.post(f"/api/testing/baseline/{project['id']}/scan", headers=headers)
        assert first_scan.json()["generated"] == 10

        # A real new commit touching an auth-mapped file.
        (target / "src" / "auth_login.js").write_text("export function login() { return true; }\n")
        subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "feat: add login"], cwd=target, check=True, capture_output=True)

        select_resp = await client.get(f"/api/testing/selection/{project['id']}/select", headers=headers)
        assert select_resp.status_code == 200
        body = select_resp.json()

        assert body["changed_files"] == ["src/auth_login.js"]
        assert body["relevant_categories"] == ["auth"]

        selected_categories = {s["category"] for s in body["selected"]}
        assert "auth" in selected_categories
        assert "integration" in selected_categories  # proximity fallback always included
        auth_entry = next(s for s in body["selected"] if s["category"] == "auth")
        assert auth_entry["category_weight"] == 1.0
        integration_entry = next(s for s in body["selected"] if s["category"] == "integration")
        assert integration_entry["category_weight"] == 0.5

        # Categories with no relevance were skipped, not silently included.
        assert body["estimated_tests_skipped"] > 0
        assert len(body["selected"]) + len(body["skipped"]) == 10

        coverage_resp = await client.get(f"/api/testing/selection/{project['id']}/coverage-gaps", headers=headers)
        assert coverage_resp.json() == []  # full baseline covered every category

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_selection_rejects_without_baseline_reference():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers, _ = await _login_and_headers(client, "selectionnobasis@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "No Baseline Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        resp = await client.get(f"/api/testing/selection/{project['id']}/select", headers=headers)
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_detection_finds_identical_doc_driven_titles():
    from tests.conftest_docs import build_docx_bytes

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers, _ = await _login_and_headers(client, "duplicates@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Duplicates Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        docx_bytes = build_docx_bytes(["Users should be able to log in with a valid email and password."])
        files = {"file": ("prd.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        await client.post(f"/api/testing/doc-driven/{project['id']}/upload", files=files, headers=headers)
        await client.post(f"/api/testing/doc-driven/{project['id']}/upload", files=files, headers=headers)

        dup_resp = await client.get(f"/api/testing/selection/{project['id']}/duplicates", headers=headers)
        duplicates = dup_resp.json()
        assert len(duplicates) == 1
        assert duplicates[0]["similarity"] == 1.0


@pytest.mark.asyncio
async def test_flaky_report_honest_about_insufficient_history_and_real_when_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers, org_id = await _login_and_headers(client, "flaky@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Flaky Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

    db = get_database()
    case_stable = TestCase(
        organization_id=org_id, project_id=project["id"], title="Stable test", type="unit",
        priority="medium", expected_result="passes", created_by="tester",
    )
    case_flaky = TestCase(
        organization_id=org_id, project_id=project["id"], title="Flaky test", type="unit",
        priority="medium", expected_result="passes", created_by="tester",
    )
    await db.test_cases.insert_one(case_stable.model_dump(by_alias=True))
    await db.test_cases.insert_one(case_flaky.model_dump(by_alias=True))

    # Stable: only 1 real run — insufficient history, must be honest about it.
    await db.test_results.insert_one(TestResult(
        organization_id=org_id, project_id=project["id"], run_id=new_id(),
        test_case_id=case_stable.id, status="passed",
    ).model_dump(by_alias=True))

    # Flaky: 4 real runs alternating pass/fail — genuinely flaky.
    for status in ["passed", "failed", "passed", "failed"]:
        await db.test_results.insert_one(TestResult(
            organization_id=org_id, project_id=project["id"], run_id=new_id(),
            test_case_id=case_flaky.id, status=status,
        ).model_dump(by_alias=True))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers2, _ = await _login_and_headers(client, "flaky@example.com")
        resp = await client.get(f"/api/testing/selection/{project['id']}/flaky-report", headers=headers2)
        report = {r["title"]: r for r in resp.json()}

        assert report["Stable test"]["flaky_score"] is None
        assert "not available" in report["Stable test"]["status"]

        assert report["Flaky test"]["flaky_score"] == 1.0  # every consecutive run changed status
        assert report["Flaky test"]["run_count"] == 4
