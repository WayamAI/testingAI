from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RawFinding:
    tool: str
    severity: str
    file: str | None
    line: int | None
    issue: str
    evidence: str | None
    recommendation: str | None


class SecurityScanUnavailable(Exception):
    """Raised with a specific reason (missing binary, no applicable
    manifest) — always shown to the user, never silently swallowed."""


class SecurityScanProvider(ABC):
    name: str

    @abstractmethod
    def applies_to(self, workspace_path: Path) -> bool: ...

    @abstractmethod
    async def scan(self, workspace_path: Path) -> list[RawFinding]: ...
