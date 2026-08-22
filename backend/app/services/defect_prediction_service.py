from app.database.mongo import get_database
from app.engines.ai.base import RiskFileSummary, RiskNarrativeInput
from app.engines.ai.factory import generate_risk_narrative_with_fallback
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.file_risk_score import FileRiskScore, risk_label
from app.services import git_mining


class ProjectNotConnected(Exception):
    pass


class NotAGitRepo(Exception):
    pass


def _normalize(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0 if value <= lo else 1.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


async def run_defect_prediction(org_id: str, project_id: str) -> dict:
    workspace = workspace_path(project_id)
    if not workspace.exists():
        raise ProjectNotConnected("This project has no connected workspace to mine.")
    if not await git_mining.is_git_repo(workspace):
        raise NotAGitRepo("The connected workspace is not a git repository (real commit history required).")

    file_metrics = await git_mining.mine_file_metrics(workspace)
    if not file_metrics:
        return {"scan_id": new_id(), "files_analyzed": 0, "top_files": [], "narrative": "No file history found.", "source": "none"}

    freqs = [m.change_frequency for m in file_metrics.values()]
    churns = [m.churn for m in file_metrics.values()]
    author_counts = [len(m.authors) for m in file_metrics.values()]
    freq_lo, freq_hi = min(freqs), max(freqs)
    churn_lo, churn_hi = min(churns), max(churns)
    author_lo, author_hi = min(author_counts), max(author_counts)

    db = get_database()
    scan_id = new_id()
    scored: list[FileRiskScore] = []

    for path, m in file_metrics.items():
        norm_freq = _normalize(m.change_frequency, freq_lo, freq_hi)
        norm_churn = _normalize(m.churn, churn_lo, churn_hi)
        norm_authors = _normalize(len(m.authors), author_lo, author_hi)
        score = 0.30 * norm_freq + 0.35 * m.bug_fix_ratio + 0.20 * norm_churn + 0.15 * norm_authors

        record = FileRiskScore(
            organization_id=org_id,
            project_id=project_id,
            scan_id=scan_id,
            file_path=path,
            change_frequency=m.change_frequency,
            bug_fix_ratio=round(m.bug_fix_ratio, 4),
            churn=m.churn,
            author_count=len(m.authors),
            risk_score=round(score, 4),
            risk_label=risk_label(score),
        )
        await db.file_risk_scores.insert_one(record.model_dump(by_alias=True))
        scored.append(record)

    scored.sort(key=lambda r: r.risk_score, reverse=True)
    top = scored[:5]

    narrative_input = RiskNarrativeInput(top_files=[
        RiskFileSummary(
            path=r.file_path, risk_score=r.risk_score, risk_label=r.risk_label,
            change_frequency=r.change_frequency, bug_fix_ratio=r.bug_fix_ratio,
            churn=r.churn, author_count=r.author_count,
        ) for r in top
    ])
    narrative, source = await generate_risk_narrative_with_fallback(narrative_input)

    return {
        "scan_id": scan_id,
        "files_analyzed": len(scored),
        "top_files": [r.model_dump() for r in top],
        "narrative": narrative.narrative,
        "source": source,
    }


async def list_risk_scores(org_id: str, project_id: str) -> list[FileRiskScore]:
    db = get_database()
    cursor = db.file_risk_scores.find({"organization_id": org_id, "project_id": project_id}).sort("risk_score", -1)
    return [FileRiskScore.model_validate(d) async for d in cursor]


async def get_latest_scan_id(org_id: str, project_id: str) -> str | None:
    db = get_database()
    doc = await db.file_risk_scores.find_one(
        {"organization_id": org_id, "project_id": project_id}, sort=[("created_at", -1)]
    )
    return doc["scan_id"] if doc else None
