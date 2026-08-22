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
async def test_defect_prediction_scores_real_git_history(tmp_path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "defectpred@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Risky Repo Project", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        # Materialize the real crafted-history repo directly into this
        # project's workspace (bypassing git-clone network I/O, which the
        # detection/execution flows already cover elsewhere).
        repo = build_risky_repo(tmp_path)
        target = workspace_path(project["id"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo, target)

        scan_resp = await client.post(f"/api/testing/defect-prediction/{project['id']}/scan", headers=headers)
        assert scan_resp.status_code == 200
        summary = scan_resp.json()
        assert summary["files_analyzed"] == 2
        assert summary["source"] in ("ai", "demo_fallback")
        assert "risky.js" in summary["narrative"] or any("risky" in f["file_path"] for f in summary["top_files"])

        top_paths = {f["file_path"]: f["risk_score"] for f in summary["top_files"]}
        assert top_paths["src/risky.js"] > top_paths["src/stable.js"]

        scores_resp = await client.get(f"/api/testing/defect-prediction/{project['id']}/scores", headers=headers)
        scores = scores_resp.json()
        assert len(scores) == 2
        assert scores[0]["file_path"] == "src/risky.js"  # sorted by risk_score desc
        assert scores[0]["risk_label"] in ("low", "medium", "high", "critical")

    shutil.rmtree(target, ignore_errors=True)


@pytest.mark.asyncio
async def test_defect_prediction_rejects_unconnected_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _login_and_headers(client, "defectpredunconnected@example.com")
        create_resp = await client.post(
            "/api/projects", json={"name": "Never Connected DP", "project_type": "web_application"}, headers=headers
        )
        project = create_resp.json()

        scan_resp = await client.post(f"/api/testing/defect-prediction/{project['id']}/scan", headers=headers)
        assert scan_resp.status_code == 422
