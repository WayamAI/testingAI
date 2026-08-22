from app.models.base import MongoDocument


class QualityScore(MongoDocument):
    organization_id: str
    project_id: str
    overall: int
    functional: int
    reliability: int
    security: int
    performance: int
    accessibility: int
    coverage: int
