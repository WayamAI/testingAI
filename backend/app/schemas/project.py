from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    project_type: str


class ProjectOut(BaseModel):
    id: str
    name: str
    project_type: str
    organization_id: str
    source: str = "demo"
    intake_status: str = "none"
    intake_error: str | None = None
    repo_url: str | None = None
    detected_language: str | None = None
    detected_test_framework: str | None = None
