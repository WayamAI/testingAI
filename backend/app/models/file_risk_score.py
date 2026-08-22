from app.models.base import MongoDocument


def risk_label(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.5:
        return "high"
    if score >= 0.25:
        return "medium"
    return "low"


class FileRiskScore(MongoDocument):
    organization_id: str
    project_id: str
    scan_id: str
    file_path: str
    change_frequency: int
    bug_fix_ratio: float
    churn: int
    author_count: int
    risk_score: float  # 0-1, weighted+normalized
    risk_label: str  # low|medium|high|critical
