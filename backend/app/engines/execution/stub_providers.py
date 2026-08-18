from app.engines.execution.base import ExecutionProvider


class _NotImplementedExecutionProvider(ExecutionProvider):
    async def run_suite(self, run_id: str, case_ids: list[str]):
        raise NotImplementedError("Provider not yet implemented")
        yield  # pragma: no cover - unreachable, keeps this an async generator


class PlaywrightExecutionProvider(_NotImplementedExecutionProvider):
    pass


class APIExecutionProvider(_NotImplementedExecutionProvider):
    pass


class MobileExecutionProvider(_NotImplementedExecutionProvider):
    pass


class PerformanceExecutionProvider(_NotImplementedExecutionProvider):
    pass
