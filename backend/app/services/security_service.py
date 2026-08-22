from app.database.mongo import get_database
from app.detection.rules import ApplicationProfile  # noqa: F401  (type reference only)
from app.engines.security.base import SecurityScanUnavailable
from app.engines.security.dependency_provider import NpmAuditProvider, PipAuditProvider
from app.engines.security.semgrep_provider import SemgrepProvider
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.security_finding import SecurityFinding

_PROVIDERS = [SemgrepProvider(), PipAuditProvider(), NpmAuditProvider()]


class ProjectNotConnected(Exception):
    pass


async def run_security_scan(org_id: str, project_id: str) -> dict:
    """Runs every applicable SecurityScanProvider against the project's
    workspace, persists real findings, and returns a summary including
    which providers ran vs. were unavailable and why. Never fabricates a
    finding."""
    workspace = workspace_path(project_id)
    if not workspace.exists():
        raise ProjectNotConnected("This project has no connected workspace to scan.")

    db = get_database()
    scan_id = new_id()
    provider_status: dict[str, str] = {}
    total_findings = 0

    for provider in _PROVIDERS:
        if not provider.applies_to(workspace):
            provider_status[provider.name] = "not_applicable"
            continue
        try:
            raw_findings = await provider.scan(workspace)
        except SecurityScanUnavailable as exc:
            provider_status[provider.name] = f"requires_configuration: {exc}"
            continue

        for raw in raw_findings:
            finding = SecurityFinding(
                organization_id=org_id,
                project_id=project_id,
                scan_id=scan_id,
                tool=raw.tool,
                severity=raw.severity,
                file=raw.file,
                line=raw.line,
                issue=raw.issue,
                evidence=raw.evidence,
                recommendation=raw.recommendation,
            )
            await db.security_findings.insert_one(finding.model_dump(by_alias=True))
            total_findings += 1
        provider_status[provider.name] = f"ran ({len(raw_findings)} findings)"

    summary = {"scan_id": scan_id, "provider_status": provider_status, "total_findings": total_findings}
    await db.security_scans.insert_one({
        "_id": scan_id,
        "organization_id": org_id,
        "project_id": project_id,
        **summary,
    })
    return summary


async def has_run_scan(org_id: str, project_id: str) -> bool:
    db = get_database()
    doc = await db.security_scans.find_one({"organization_id": org_id, "project_id": project_id})
    return doc is not None


async def open_finding_counts(org_id: str, project_id: str) -> dict[str, int]:
    db = get_database()
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    async for doc in db.security_findings.find({"organization_id": org_id, "project_id": project_id}):
        sev = doc.get("severity", "low")
        if sev in counts:
            counts[sev] += 1
    return counts


async def list_findings(org_id: str, project_id: str) -> list[SecurityFinding]:
    db = get_database()
    cursor = db.security_findings.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [SecurityFinding.model_validate(d) async for d in cursor]
