"""Builds a real, bounded text summary of a workspace — file tree plus key
manifest contents — for feeding to AI baseline test generation. Never
fabricates structure; everything here is read from the actual workspace.
"""
from pathlib import Path

_EXCLUDED_DIRS = {"node_modules", ".git", ".wayam-venv", "dist", "__pycache__", ".venv", "build"}
_MAX_FILES = 200


def _list_files(workspace: Path) -> list[str]:
    paths = []
    for p in workspace.rglob("*"):
        if p.is_dir():
            continue
        if any(part in _EXCLUDED_DIRS for part in p.parts):
            continue
        paths.append(str(p.relative_to(workspace)))
        if len(paths) >= _MAX_FILES:
            break
    return sorted(paths)


def build_summary(workspace: Path) -> str:
    files = _list_files(workspace)
    lines = [f"File tree ({len(files)} file(s), truncated at {_MAX_FILES}):"]
    lines.extend(f"  {f}" for f in files)

    package_json = workspace / "package.json"
    if package_json.exists():
        lines.append("\npackage.json:")
        lines.append(package_json.read_text()[:2000])

    readme = next((workspace / n for n in ("README.md", "readme.md") if (workspace / n).exists()), None)
    if readme:
        lines.append("\nREADME excerpt:")
        lines.append(readme.read_text()[:1500])

    return "\n".join(lines)
