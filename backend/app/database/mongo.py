from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(get_settings().mongodb_uri, serverSelectionTimeoutMS=3000)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[get_settings().database_name]


async def ping_database() -> bool:
    try:
        await get_client().admin.command("ping")
        return True
    except Exception:
        return False
