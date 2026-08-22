"""Feature 6: Intelligent Test Selection & Optimization.

Maps real changed files (git diff) to relevant baseline tests via category
overlap + a real risk-score weight (reusing feature 4's mined data),
producing an explainable per-test score. Also finds real duplicate tests
and real category coverage gaps. Flaky detection only runs where real
TestResult history exists — honestly "not available" otherwise, never
estimated.
"""
import difflib

from app.database.mongo import get_database
from app.intake.workspace import workspace_path
from app.services import git_mining
from app.services.category_inference import infer_categories_from_changed_files
from app.services.playwright_codegen import CATEGORIES

FLAKY_MIN_HISTORY = 3
_DUPLICATE_SIMILARITY_THRESHOLD = 0.85


class ProjectNotConnected(Exception):
    pass


class NoBaselineReference(Exception):
    pass


async def select_tests(org_id: str, project_id: str, since_commit: str | None = None) -> dict:
    workspace = workspace_path(project_id)
    if not workspace.exists():
        raise ProjectNotConnected("This project has no connected workspace.")

    db = get_database()
    if since_commit is None:
        project_doc = await db.projects.find_one({"_id": project_id, "organization_id": org_id})
        since_commit = project_doc.get("baseline_last_scanned_commit") if project_doc else None
    if since_commit is None:
        raise NoBaselineReference("No baseline reference commit available — run a Repo Test Baseline scan first, or pass since_commit explicitly.")

    changed_files = await git_mining.get_changed_files(workspace, since_commit)
    relevant_categories = infer_categories_from_changed_files(changed_files) if changed_files else []

    risk_by_file = {
        doc["file_path"]: doc["risk_score"]
        async for doc in db.file_risk_scores.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    }
    changed_risk_scores = [risk_by_file[f] for f in changed_files if f in risk_by_file]
    avg_risk = sum(changed_risk_scores) / len(changed_risk_scores) if changed_risk_scores else 0.3  # unknown risk baseline

    all_tests = [doc async for doc in db.generated_tests.find({"organization_id": org_id, "project_id": project_id})]

    scored = []
    skipped = []
    for t in all_tests:
        if t["category"] in relevant_categories:
            category_weight = 1.0
            reason = f"direct category match: changed files map to '{t['category']}'"
        elif t["category"] == "integration":
            category_weight = 0.5
            reason = "proximity match: integration tests cover cross-cutting changes"
        else:
            skipped.append({"test_id": t["_id"], "title": t["title"], "category": t["category"], "reason": "no relevant changed files for this category"})
            continue

        score = round(0.6 * category_weight + 0.4 * avg_risk, 4)
        scored.append({
            "test_id": t["_id"], "title": t["title"], "category": t["category"],
            "score": score, "category_weight": category_weight, "risk_weight": round(avg_risk, 4), "reason": reason,
        })

    scored.sort(key=lambda s: s["score"], reverse=True)

    return {
        "since_commit": since_commit,
        "changed_files": changed_files,
        "relevant_categories": relevant_categories,
        "selected": scored,
        "skipped": skipped,
        "estimated_tests_skipped": len(skipped),
    }


async def find_duplicates(org_id: str, project_id: str) -> list[dict]:
    db = get_database()
    tests = [doc async for doc in db.generated_tests.find({"organization_id": org_id, "project_id": project_id})]
    duplicates = []
    seen_pairs = set()
    for i, a in enumerate(tests):
        for b in tests[i + 1:]:
            pair_key = tuple(sorted((a["_id"], b["_id"])))
            if pair_key in seen_pairs:
                continue
            similarity = difflib.SequenceMatcher(None, a["title"].lower(), b["title"].lower()).ratio()
            if similarity >= _DUPLICATE_SIMILARITY_THRESHOLD:
                seen_pairs.add(pair_key)
                duplicates.append({
                    "test_a_id": a["_id"], "test_a_title": a["title"],
                    "test_b_id": b["_id"], "test_b_title": b["title"],
                    "similarity": round(similarity, 3),
                })
    return duplicates


async def find_coverage_gaps(org_id: str, project_id: str) -> list[str]:
    db = get_database()
    present = {
        doc["_id"] async for doc in db.generated_tests.aggregate([
            {"$match": {"organization_id": org_id, "project_id": project_id}},
            {"$group": {"_id": "$category"}},
        ])
    }
    return [c for c in CATEGORIES if c not in present]


async def flaky_report(org_id: str, project_id: str) -> list[dict]:
    """Real flaky-score computation for every TestCase with >= FLAKY_MIN_HISTORY
    real TestResults; honestly reports 'not available' for the rest instead
    of guessing."""
    db = get_database()
    report = []
    async for case in db.test_cases.find({"organization_id": org_id, "project_id": project_id}):
        results = [
            r async for r in db.test_results.find(
                {"organization_id": org_id, "project_id": project_id, "test_case_id": case["_id"]}
            ).sort("created_at", 1)
        ]
        if len(results) < FLAKY_MIN_HISTORY:
            report.append({
                "test_case_id": case["_id"], "title": case["title"],
                "flaky_score": None, "run_count": len(results),
                "status": f"not available: only {len(results)} run(s), needs >= {FLAKY_MIN_HISTORY}",
            })
            continue

        statuses = [r["status"] for r in results]
        transitions = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i - 1])
        flaky_score = round(transitions / (len(statuses) - 1), 4)
        report.append({
            "test_case_id": case["_id"], "title": case["title"],
            "flaky_score": flaky_score, "run_count": len(results), "status": "available",
        })
    return report
