import io
import zipfile

import pytest

from app.intake.zip_extract import ZipExtractError, extract_zip
from app.intake.git_clone import GitCloneError, clone_repository


def _make_zip(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_extract_zip_succeeds_for_a_normal_archive():
    data = _make_zip({"package.json": b'{"name": "x", "scripts": {"test": "jest"}}'})
    workspace = extract_zip("test-project-normal", data)
    assert (workspace / "package.json").exists()


def test_extract_zip_rejects_path_traversal():
    data = _make_zip({"../../etc/evil": b"pwned"})
    with pytest.raises(ZipExtractError, match="escapes"):
        extract_zip("test-project-traversal", data)


def test_extract_zip_rejects_invalid_archive():
    with pytest.raises(ZipExtractError, match="not a valid ZIP"):
        extract_zip("test-project-badzip", b"not a zip file")


@pytest.mark.asyncio
async def test_clone_rejects_malformed_url():
    with pytest.raises(GitCloneError):
        await clone_repository("test-project-badurl", "not-a-url")


@pytest.mark.asyncio
async def test_clone_reports_reason_for_unreachable_host():
    with pytest.raises(GitCloneError):
        await clone_repository(
            "test-project-unreachable",
            "https://this-host-does-not-exist-wayam-testing.invalid/org/repo",
        )
