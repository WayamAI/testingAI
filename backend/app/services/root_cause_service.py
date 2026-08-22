"""Feature 5: AI Root Cause Analysis — extends the existing failure
analysis with real git correlation: ranks recent real commits by file-path
overlap with the failure's stack trace, and feeds the real diff of the
top candidate to the AI (with a deterministic fallback that still narrates
around the real correlated commit).
"""
import re

from app.database.mongo import get_database
from app.engines.ai.base import CommitSummary, FailureContext, GitCorrelationContext
from app.engines.ai.factory import analyze_failure_with_fallback, analyze_failure_with_git_fallback
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.root_cause_analysis import RootCauseAnalysis
from app.services import git_mining

_PATH_PATTERN = re.compile(r"[\w./-]+\.(?:js|jsx|ts|tsx|py|java|go|rb|php)\b")


def _extract_referenced_paths(stack_trace: str) -> set[str]:
    return {m.group(0) for m in _PATH_PATTERN.finditer(stack_trace)}


def _rank_candidates(commits: list, referenced_paths: set[str]):
    """Real ranking: most file-path overlap with the stack trace wins;
    ties broken by recency (commits list is already newest-first).
    Falls back to the most recent commit if nothing overlaps — still a
    real commit, just a lower-confidence correlation."""
    if not commits:
        return None

    def overlap_score(commit) -> int:
        return sum(1 for f in commit.files if any(f.endswith(p) or p.endswith(f) for p in referenced_paths))

    scored = sorted(commits, key=overlap_score, reverse=True)
    return scored[0] if scored else commits[0]


async def analyze_with_correlation(
    org_id: str, project_id: str, error_message: str, stack_trace: str, test_case_title: str
) -> dict:
    context = FailureContext(error_message=error_message, stack_trace=stack_trace, test_case_title=test_case_title)
    workspace = workspace_path(project_id)

    if not workspace.exists() or not await git_mining.is_git_repo(workspace):
        analysis, source = await analyze_failure_with_fallback(context)
        result = {
            "root_cause": analysis.root_cause, "confidence": analysis.confidence,
            "recommendation": analysis.recommendation, "affected_component": analysis.affected_component,
            "likely_commit_sha": None, "likely_commit_message": None, "source": source,
            "git_correlation_available": False,
        }
    else:
        commits = await git_mining.get_recent_commits(workspace, limit=15)
        referenced_paths = _extract_referenced_paths(stack_trace)
        top_candidate = _rank_candidates(commits, referenced_paths)

        diff = await git_mining.get_commit_diff(workspace, top_candidate.sha) if top_candidate else ""
        git_context = GitCorrelationContext(
            candidate_commits=[CommitSummary(sha=c.sha, author=c.author, message=c.message) for c in commits],
            top_candidate_sha=top_candidate.sha if top_candidate else None,
            top_candidate_diff=diff,
        )
        analysis, source = await analyze_failure_with_git_fallback(context, git_context)
        result = {
            "root_cause": analysis.root_cause, "confidence": analysis.confidence,
            "recommendation": analysis.recommendation, "affected_component": analysis.affected_component,
            "likely_commit_sha": analysis.likely_commit_sha, "likely_commit_message": analysis.likely_commit_message,
            "source": source, "git_correlation_available": True,
        }

    db = get_database()
    record = RootCauseAnalysis(
        organization_id=org_id, project_id=project_id,
        error_message=error_message, stack_trace=stack_trace, test_case_title=test_case_title,
        root_cause=result["root_cause"], confidence=result["confidence"],
        recommendation=result["recommendation"], affected_component=result["affected_component"],
        likely_commit_sha=result["likely_commit_sha"], likely_commit_message=result["likely_commit_message"],
        source=result["source"],
    )
    await db.root_cause_analyses.insert_one(record.model_dump(by_alias=True))
    result["id"] = record.id
    return result


async def list_history(org_id: str, project_id: str) -> list[RootCauseAnalysis]:
    db = get_database()
    cursor = db.root_cause_analyses.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [RootCauseAnalysis.model_validate(d) async for d in cursor]
