from pydantic import BaseModel


class DefectCreate(BaseModel):
    project_id: str
    title: str
    description: str
    severity: str
    priority: str
    related_test_result_id: str | None = None
    related_test_case_id: str | None = None


class DefectOut(BaseModel):
    id: str
    project_id: str
    title: str
    severity: str
    priority: str
    status: str


class QualityScoreOut(BaseModel):
    overall: int
    functional: int
    reliability: int
    security: int
    performance: int
    accessibility: int
    coverage: int


class ReleaseReadinessOut(BaseModel):
    status: str
    pass_rate: float
    critical_defects: int
    quality_score: int
    gate_violations: list[str]
