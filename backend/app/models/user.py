from app.models.base import MongoDocument


class User(MongoDocument):
    email: str
    hashed_password: str
    name: str
    organization_id: str
    role: str = "qa_engineer"  # owner|administrator|engineering_manager|qa_manager|qa_engineer|developer|security_engineer|product_manager|viewer
