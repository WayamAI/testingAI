from app.models.base import MongoDocument


class SecurityFinding(MongoDocument):
    organization_id: str
    project_id: str
    scan_id: str
    tool: str  # semgrep|pip-audit|npm-audit
    severity: str  # critical|high|medium|low|info
    file: str | None = None
    line: int | None = None
    issue: str
    evidence: str | None = None
    recommendation: str | None = None
