from app.models.base import MongoDocument


class SelfHealAttempt(MongoDocument):
    organization_id: str
    project_id: str
    url: str
    original_selector: str
    failure_context: str
    proposed_selector: str
    candidate_index: int
    ai_confidence: float
    ai_reasoning: str
    source: str  # ai|demo_fallback
    live_validation_count: int  # how many elements the proposal resolved to when validated
    status: str = "proposed"  # proposed|approved|rejected
    target_file: str | None = None
    target_line: int | None = None
    applied: bool = False
