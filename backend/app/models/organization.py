from app.models.base import MongoDocument


class Organization(MongoDocument):
    name: str
    slug: str | None = None
