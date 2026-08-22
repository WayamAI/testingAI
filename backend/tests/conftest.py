import shutil

import pytest

from app.intake.workspace import WORKSPACES_ROOT


@pytest.fixture(autouse=True, scope="session")
def _cleanup_test_workspaces():
    yield
    if WORKSPACES_ROOT.exists():
        for entry in WORKSPACES_ROOT.iterdir():
            if entry.name.startswith("test-project-"):
                shutil.rmtree(entry, ignore_errors=True)
