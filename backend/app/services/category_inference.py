"""Shared changed-file -> baseline-category heuristic, used by both
Repo Test Baseline (feature 1, incremental re-scan) and Intelligent Test
Selection (feature 6, mapping changed files to relevant tests).
"""
_CATEGORY_PATH_HINTS = {
    "auth": ["auth", "login", "session", "password"],
    "api": ["api", "route", "endpoint", "controller"],
    "crud": ["model", "crud", "repository", "service"],
    "ui_form": ["form"],
    "ui_navigation": ["nav", "router", "page"],
    "ui_component": ["component"],
    "performance": ["perf"],
    "accessibility": ["a11y", "accessib"],
}


def infer_categories_from_changed_files(changed_files: list[str]) -> list[str]:
    matched: list[str] = []
    for path in changed_files:
        lowered = path.lower()
        for category, hints in _CATEGORY_PATH_HINTS.items():
            if any(hint in lowered for hint in hints) and category not in matched:
                matched.append(category)
    return matched or ["integration"]  # a real change with no keyword match still deserves a baseline check
