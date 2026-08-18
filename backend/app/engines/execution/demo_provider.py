import asyncio
import random
from app.engines.execution.base import ExecutionProvider, ExecutionEvent


class DemoExecutionProvider(ExecutionProvider):
    async def run_suite(self, run_id: str, case_ids: list[str]):
        yield ExecutionEvent(type="status", status="preparing")
        await asyncio.sleep(0.05)
        yield ExecutionEvent(type="status", status="running")

        rng = random.Random(run_id)
        forced_failure_index = 0 if case_ids else None

        for idx, case_id in enumerate(case_ids):
            await asyncio.sleep(0.05)
            duration = rng.randint(80, 1800)
            if idx == forced_failure_index:
                status = "failed"
            else:
                roll = rng.random()
                status = "passed" if roll > 0.25 else ("flaky" if roll > 0.15 else "failed" if roll > 0.05 else "skipped")

            error_message = None
            stack_trace = None
            if status in ("failed", "flaky"):
                error_message = rng.choice([
                    "Timeout waiting for element #submit-payment",
                    "Expected status 200 but received 500",
                    "AssertionError: expected 'Order Confirmed' but got 'Order Pending'",
                ])
                stack_trace = f"at test_case_{case_id}.spec.ts:{rng.randint(10, 120)}"

            yield ExecutionEvent(
                type="result",
                test_case_id=case_id,
                status=status,
                duration_ms=duration,
                error_message=error_message,
                stack_trace=stack_trace,
            )

        yield ExecutionEvent(type="status", status="completed")
