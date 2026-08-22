from arq.connections import RedisSettings


async def startup(ctx):
    print("worker started")


async def shutdown(ctx):
    print("worker stopped")


async def noop(ctx):
    """Placeholder task. This sub-project's execution runs synchronously in the
    backend's WebSocket handler (see backend/app/routes/websocket_execution.py);
    no background jobs are enqueued yet. arq requires at least one registered
    function to boot, so this keeps the worker process alive as scaffolding for
    the async task types a later sub-project will add (report generation,
    scheduled runs, etc.)."""
    return None


class WorkerSettings:
    functions = [noop]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn("redis://localhost:6379")
