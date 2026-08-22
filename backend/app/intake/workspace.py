"""Per-project isolated workspace directories.

Every connected project (git URL or ZIP) is materialized under
`backend/workspaces/{project_id}/` and never executed in place elsewhere.
Callers must always go through `workspace_path()` / `reset_workspace()`
rather than constructing paths themselves, so the isolation boundary stays
in one place.
"""
import shutil
from pathlib import Path

WORKSPACES_ROOT = Path(__file__).resolve().parent.parent.parent / "workspaces"


def workspace_path(project_id: str) -> Path:
    """Return the isolated workspace directory for a project, creating the
    workspaces root if needed. Does not create the project directory itself
    — callers create it as part of clone/extract so a half-created dir is
    never mistaken for a valid workspace."""
    WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
    return WORKSPACES_ROOT / project_id


def reset_workspace(project_id: str) -> Path:
    """Remove any existing workspace for this project and return a fresh,
    empty directory ready for clone/extract."""
    path = workspace_path(project_id)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path
