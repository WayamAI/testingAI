import threading
import time

import pytest
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.services.dom_scan_service import DomScanError, scan_live_dom

_HTML = """
<!doctype html><html><body>
  <input id="email" name="email" placeholder="Email address" />
  <button id="submit-payment">Submit Payment</button>
  <a href="/help">Help</a>
</body></html>
"""


@pytest.fixture(scope="module")
def live_target_server():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return _HTML

    config = uvicorn.Config(app, host="127.0.0.1", port=8766, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    yield "http://127.0.0.1:8766"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.mark.asyncio
async def test_scan_live_dom_finds_real_elements(live_target_server):
    candidates = await scan_live_dom(live_target_server)
    tags = {c.tag for c in candidates}
    assert "input" in tags
    assert "button" in tags
    assert "a" in tags

    submit_button = next(c for c in candidates if c.selector_hint == "#submit-payment")
    assert submit_button.text == "Submit Payment"


@pytest.mark.asyncio
async def test_scan_live_dom_raises_for_unreachable_url():
    with pytest.raises(DomScanError):
        await scan_live_dom("http://127.0.0.1:9999/definitely-not-running")
