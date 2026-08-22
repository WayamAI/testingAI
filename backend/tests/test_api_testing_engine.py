import asyncio
import threading
from pathlib import Path

import pytest
import uvicorn
from fastapi import FastAPI

from app.engines.api_testing.openapi_provider import discover_spec, run_get_endpoints

FIXTURES = Path(__file__).parent / "fixtures"


def _make_target_app() -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    return app


@pytest.fixture(scope="module")
def live_target_server():
    """A real uvicorn server on a real socket — proves run_get_endpoints
    makes genuine HTTP requests, not a mocked/ASGI-transport call."""
    config = uvicorn.Config(_make_target_app(), host="127.0.0.1", port=8765, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    import time
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)

    yield "http://127.0.0.1:8765"

    server.should_exit = True
    thread.join(timeout=5)


def test_discover_spec_finds_openapi_json():
    spec = discover_spec(FIXTURES / "api_project")
    assert spec is not None
    assert "/ping" in spec["paths"]


@pytest.mark.asyncio
async def test_run_get_endpoints_makes_real_requests_and_skips_parameterized_paths(live_target_server):
    spec = discover_spec(FIXTURES / "api_project")
    results = await run_get_endpoints(spec, live_target_server)

    by_name = {r.name: r for r in results}
    assert by_name["GET /ping"].status == "passed"
    assert by_name["GET /ping"].status_code == 200

    # Parameterized path is skipped in this first cut, not faked.
    assert by_name["GET /items/{item_id}"].status == "failed"
    assert "requires path/query parameters" in by_name["GET /items/{item_id}"].error_message
