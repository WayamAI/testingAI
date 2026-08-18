from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    project_type: str


class ProjectOut(BaseModel):
    id: str
    name: str
    project_type: str
    organization_id: str
