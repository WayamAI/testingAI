from app.database.mongo import get_database
from app.services.defect_service import count_open_critical
from app.services.security_service import has_run_scan, open_finding_counts


async def _pass_rate(org_id: str, project_id: str) -> float:
    db = get_database()
    total = await db.test_results.count_documents({"organization_id": org_id, "project_id": project_id})
    if total == 0:
        return 1.0
    passed = await db.test_results.count_documents({"organization_id": org_id, "project_id": project_id, "status": "passed"})
    return round(passed / total, 4)


async def compute_quality_score(org_id: str, project_id: str) -> dict:
    db = get_database()
    pass_rate = await _pass_rate(org_id, project_id)
    critical = await count_open_critical(org_id, project_id)
    flaky = await db.test_results.count_documents({"organization_id": org_id, "project_id": project_id, "status": "flaky"})

    functional = round(pass_rate * 100)
    reliability = max(0, 100 - flaky * 5)

    if await has_run_scan(org_id, project_id):
        counts = await open_finding_counts(org_id, project_id)
        security = max(0, 100 - counts["critical"] * 25 - counts["high"] * 12 - counts["medium"] * 4 - counts["low"] * 1)
    else:
        security = 92  # no scan run yet this project; conservative unverified baseline

    performance = 83  # no performance engine this sub-project — still a fixed baseline (spec §21, deferred)
    accessibility = 79  # no accessibility engine this sub-project — still a fixed baseline (spec §17, deferred)
    coverage = 94 if pass_rate > 0 else 0  # placeholder proxy until true coverage engine lands

    penalties = critical * 10
    overall = max(0, round((functional + reliability + security + performance + accessibility + coverage) / 6) - penalties)

    return {
        "overall": overall,
        "functional": functional,
        "reliability": reliability,
        "security": security,
        "performance": performance,
        "accessibility": accessibility,
        "coverage": coverage,
    }


async def compute_release_readiness(org_id: str, project_id: str) -> dict:
    pass_rate = await _pass_rate(org_id, project_id)
    critical = await count_open_critical(org_id, project_id)
    score = await compute_quality_score(org_id, project_id)

    violations = []
    if pass_rate < 0.95:
        violations.append(f"Pass rate {pass_rate * 100:.1f}% is below the 95% gate threshold")
    if critical > 0:
        violations.append(f"{critical} open critical defect(s) block release")

    if critical > 0:
        status = "BLOCKED"
    elif violations:
        status = "REQUIRES_REVIEW"
    elif pass_rate < 0.98:
        status = "READY_WITH_RISK"
    else:
        status = "READY"

    return {
        "status": status,
        "pass_rate": pass_rate,
        "critical_defects": critical,
        "quality_score": score["overall"],
        "gate_violations": violations,
    }
