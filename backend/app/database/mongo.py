import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings

_client: AsyncIOMotorClient | None = None
_client_loop: asyncio.AbstractEventLoop | None = None


def get_client() -> AsyncIOMotorClient:
    global _client, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    # AsyncIOMotorClient binds to the event loop it was created in. Each
    # pytest-asyncio test function runs in its own loop, so a client cached
    # from a previous loop would raise "Event loop is closed". Recreate the
    # client whenever the running loop has changed (or there is none cached).
    if _client is None or (current_loop is not None and _client_loop is not current_loop):
        if _client is not None:
            _client.close()
        _client = AsyncIOMotorClient(get_settings().mongodb_uri, serverSelectionTimeoutMS=3000)
        _client_loop = current_loop
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[get_settings().database_name]


async def ping_database() -> bool:
    try:
        await get_client().admin.command("ping")
        return True
    except Exception:
        return False
