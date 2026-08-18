from arq.connections import RedisSettings


async def startup(ctx):
    print("worker started")


async def shutdown(ctx):
    print("worker stopped")


class WorkerSettings:
    functions = []
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn("redis://localhost:6379")
