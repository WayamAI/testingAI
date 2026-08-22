"""Shared helper for building a real, throwaway git repo with crafted
commit history — used by defect prediction / root cause / test selection
tests. Not a pytest fixture module itself (imported by test files that
need it inside a tmp_path), so it isn't auto-collected.
"""
import subprocess
from pathlib import Path


def _git(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def build_risky_repo(root: Path) -> Path:
    """A real git repo where src/risky.js has 4 commits (2 of them real
    bug fixes, 2 distinct authors, real line churn) and src/stable.js has
    just 1 commit — so risky.js should score meaningfully higher."""
    repo = root / "risky_repo"
    repo.mkdir()
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "alice@example.com"], repo)
    _git(["config", "user.name", "Alice"], repo)

    (repo / "src").mkdir()
    (repo / "src" / "stable.js").write_text("export function stable() { return 1; }\n")
    (repo / "src" / "risky.js").write_text("export function risky() { return 1; }\n")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "initial commit"], repo)

    (repo / "src" / "risky.js").write_text("export function risky() { return 2; }\n")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "fix: risky returns wrong value"], repo)

    _git(["config", "user.email", "bob@example.com"], repo)
    _git(["config", "user.name", "Bob"], repo)
    (repo / "src" / "risky.js").write_text("export function risky() { return 3; }\n")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "fix bug in risky calculation"], repo)

    (repo / "src" / "risky.js").write_text(
        "export function risky() { return 4; }\nexport function extra() { return 1; }\n"
    )
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "feat: extend risky with extra helper"], repo)

    return repo
