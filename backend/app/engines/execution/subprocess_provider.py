"""Runs a connected project's real, detected test command as a supervised
child process and yields genuine pass/fail results — implements the same
ExecutionProvider interface as DemoExecutionProvider so the WebSocket live
execution view and persistence layer need no changes.

Isolation for this first cut: a dedicated workspace directory per project
plus a hard subprocess timeout. Not container/VM sandboxing — documented
limitation (see sub-project 2 spec, Non-goals).
"""
import asyncio
import shutil
from pathlib import Path

from app.detection.rules import ApplicationProfile
from app.engines.execution.base import ExecutionEvent, ExecutionProvider
from app.engines.execution.result_parsers import jest_json, pytest_junitxml

INSTALL_TIMEOUT_SECONDS = 180
RUN_TIMEOUT_SECONDS = 120


class ExecutionSetupError(Exception):
    """Install/prepare failed before any test could run — surfaced as a
    failed run, not a crash."""


async def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, f"Timed out after {timeout}s"
    return proc.returncode, stdout.decode(errors="replace")


class SubprocessExecutionProvider(ExecutionProvider):
    def __init__(self, workspace_path: Path, profile: ApplicationProfile):
        self.workspace_path = workspace_path
        self.profile = profile

    async def _install(self) -> str | None:
        """Returns an error string on failure, None on success."""
        if self.profile.package_manager == "npm":
            code, output = await _run(["npm", "install", "--no-audit", "--no-fund"], self.workspace_path, INSTALL_TIMEOUT_SECONDS)
            if code != 0:
                return f"npm install failed:\n{output[-2000:]}"
            return None

        if self.profile.package_manager == "pip":
            venv_dir = self.workspace_path / ".wayam-venv"
            if not venv_dir.exists():
                code, output = await _run(["python3", "-m", "venv", str(venv_dir)], self.workspace_path, 60)
                if code != 0:
                    return f"venv creation failed:\n{output[-2000:]}"

            pip = venv_dir / "bin" / "pip"
            reqs = self.workspace_path / "requirements.txt"
            if reqs.exists():
                code, output = await _run([str(pip), "install", "-q", "-r", "requirements.txt"], self.workspace_path, INSTALL_TIMEOUT_SECONDS)
                if code != 0:
                    return f"pip install -r requirements.txt failed:\n{output[-2000:]}"

            # pytest itself must be present even if not pinned in requirements.txt
            code, output = await _run([str(pip), "install", "-q", "pytest"], self.workspace_path, 60)
            if code != 0:
                return f"pip install pytest failed:\n{output[-2000:]}"
            return None

        return f"Unsupported package manager: {self.profile.package_manager}"

    def _resolved_command(self) -> list[str]:
        if self.profile.package_manager == "pip":
            venv_python = self.workspace_path / ".wayam-venv" / "bin" / "python"
            # test_command is ["python", "-m", "pytest", ...] — swap only
            # the interpreter for the workspace-isolated venv's own,
            # keeping "-m pytest ..." intact.
            return [str(venv_python), *self.profile.test_command[1:]]
        return self.profile.test_command

    def _report_path(self) -> Path:
        if self.profile.result_format == "jest-json":
            return self.workspace_path / "wayam-test-report.json"
        return self.workspace_path / "wayam-test-report.xml"

    async def run_suite(self, run_id: str, case_ids: list[str]):
        yield ExecutionEvent(type="status", status="preparing")

        setup_error = await self._install()
        if setup_error:
            yield ExecutionEvent(type="status", status="failed", error_message=setup_error)
            return

        yield ExecutionEvent(type="status", status="running")

        report_path = self._report_path()
        if report_path.exists():
            report_path.unlink()

        cmd = self._resolved_command()
        return_code, output = await _run(cmd, self.workspace_path, RUN_TIMEOUT_SECONDS)

        if self.profile.result_format == "jest-json":
            discovered = jest_json.parse(report_path)
        elif self.profile.result_format == "pytest-junitxml":
            discovered = pytest_junitxml.parse(report_path)
        else:
            discovered = []

        if not discovered:
            # The command ran but produced no parseable report — surface
            # the raw output as a single failed synthetic result rather
            # than silently reporting zero tests.
            yield ExecutionEvent(
                type="result",
                discovered_test_name="Test command execution",
                status="failed" if return_code != 0 else "passed",
                duration_ms=0,
                error_message=None if return_code == 0 else f"Test command exited {return_code} with no parseable report",
                stack_trace=output[-4000:] if return_code != 0 else None,
            )
        else:
            for item in discovered:
                yield ExecutionEvent(
                    type="result",
                    discovered_test_name=item.name,
                    status=item.status,
                    duration_ms=item.duration_ms,
                    error_message=item.error_message,
                    stack_trace=item.stack_trace,
                )

        yield ExecutionEvent(type="status", status="completed")
