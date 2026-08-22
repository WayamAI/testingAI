"""Real `git log` mining shared by Defect Prediction, Root Cause Analysis,
and Intelligent Test Selection. Every function here shells out to the
project's own real git history — nothing is estimated or fabricated.
"""
import asyncio
import re
from dataclasses import dataclass, field
from pathlib import Path

_FIX_PATTERN = re.compile(r"\b(fix|bug|patch|hotfix)\b", re.IGNORECASE)


@dataclass
class CommitInfo:
    sha: str
    author: str
    message: str
    files: list[str] = field(default_factory=list)


@dataclass
class FileMetrics:
    path: str
    change_frequency: int = 0
    bug_fix_commits: int = 0
    churn: int = 0
    authors: set[str] = field(default_factory=set)

    @property
    def bug_fix_ratio(self) -> float:
        if self.change_frequency == 0:
            return 0.0
        return self.bug_fix_commits / self.change_frequency


async def _run_git(args: list[str], cwd: Path) -> str:
    proc = await asyncio.create_subprocess_exec(
        "git", *args, cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode != 0:
        return ""
    return stdout.decode(errors="replace")


async def is_git_repo(workspace: Path) -> bool:
    output = await _run_git(["rev-parse", "--is-inside-work-tree"], workspace)
    return output.strip() == "true"


async def get_recent_commits(workspace: Path, limit: int = 20) -> list[CommitInfo]:
    """Real commit list, newest first, each with its real changed files."""
    raw = await _run_git(
        ["log", f"-{limit}", "--name-only", "--pretty=format:commit|%H|%an|%s"],
        workspace,
    )
    return _parse_commit_blocks(raw)


async def mine_file_metrics(workspace: Path, limit: int = 500) -> dict[str, FileMetrics]:
    """Per-file real metrics mined from `git log --numstat` over up to
    `limit` most recent commits."""
    raw = await _run_git(
        ["log", f"-{limit}", "--numstat", "--pretty=format:commit|%H|%an|%s"],
        workspace,
    )
    metrics: dict[str, FileMetrics] = {}
    current_author = None
    current_is_fix = False

    for line in raw.splitlines():
        if line.startswith("commit|"):
            _, _sha, author, message = line.split("|", 3)
            current_author = author
            current_is_fix = bool(_FIX_PATTERN.search(message))
        elif line.strip() and "\t" in line:
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, removed, path = parts
            if added == "-" or removed == "-":
                continue  # binary file, numstat can't count lines
            m = metrics.setdefault(path, FileMetrics(path=path))
            m.change_frequency += 1
            if current_is_fix:
                m.bug_fix_commits += 1
            m.churn += int(added) + int(removed)
            if current_author:
                m.authors.add(current_author)

    return metrics


def _parse_commit_blocks(raw: str) -> list[CommitInfo]:
    commits: list[CommitInfo] = []
    current: CommitInfo | None = None
    for line in raw.splitlines():
        if line.startswith("commit|"):
            if current:
                commits.append(current)
            _, sha, author, message = line.split("|", 3)
            current = CommitInfo(sha=sha, author=author, message=message)
        elif line.strip() and current is not None:
            current.files.append(line.strip())
    if current:
        commits.append(current)
    return commits


async def get_commit_diff(workspace: Path, sha: str) -> str:
    """Real `git show` diff for a single commit, truncated for prompt use."""
    raw = await _run_git(["show", "--stat", "-p", sha], workspace)
    return raw[:8000]
