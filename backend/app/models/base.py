import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MongoDocument(BaseModel):
    id: str = Field(default_factory=new_id, alias="_id")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    model_config = {"populate_by_name": True}
