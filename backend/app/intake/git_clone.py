"""Real `git clone` of a public repository into an isolated workspace."""
import asyncio
import re
from pathlib import Path

from app.intake.workspace import reset_workspace

CLONE_TIMEOUT_SECONDS = 60
_URL_PATTERN = re.compile(r"^https?://[^\s]+\.git$|^https?://[^\s]+/[^\s/]+/[^\s/]+/?$")


class GitCloneError(Exception):
    """Raised with a user-facing reason; never leaks raw subprocess output."""


def _validate_url(url: str) -> None:
    if not url or not _URL_PATTERN.match(url.strip()):
        raise GitCloneError(
            "That doesn't look like a public git repository URL "
            "(expected something like https://github.com/org/repo)."
        )


async def clone_repository(project_id: str, url: str) -> Path:
    """Clone `url` into a fresh workspace for `project_id`. Raises
    GitCloneError with a specific, actionable reason on any failure —
    never crashes the caller."""
    _validate_url(url)
    target = reset_workspace(project_id)

    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", url.strip(), str(target),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=CLONE_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise GitCloneError(
                f"Cloning timed out after {CLONE_TIMEOUT_SECONDS}s — the "
                "repository may be too large, private, or unreachable."
            )
    except FileNotFoundError:
        raise GitCloneError("git is not installed on this server.")

    if proc.returncode != 0:
        reason = stderr.decode(errors="replace").strip().splitlines()[-1] if stderr else "unknown error"
        raise GitCloneError(f"git clone failed: {reason}")

    return target
