"""Safe ZIP extraction into an isolated workspace.

Guards against path traversal (zip-slip), oversized archives, and
oversized individual entries before anything touches disk.
"""
import zipfile
from pathlib import Path

from app.intake.workspace import reset_workspace

MAX_ARCHIVE_BYTES = 200 * 1024 * 1024  # 200MB
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500MB total after extraction
MAX_FILES = 20_000


class ZipExtractError(Exception):
    """Raised with a user-facing reason."""


def _is_within(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def extract_zip(project_id: str, zip_bytes: bytes) -> Path:
    if len(zip_bytes) > MAX_ARCHIVE_BYTES:
        raise ZipExtractError(
            f"Archive is larger than the {MAX_ARCHIVE_BYTES // (1024 * 1024)}MB limit."
        )

    target = reset_workspace(project_id)
    import io

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise ZipExtractError("File is not a valid ZIP archive.")

    infos = zf.infolist()
    if len(infos) > MAX_FILES:
        raise ZipExtractError(f"Archive contains more than {MAX_FILES} files.")

    total_uncompressed = sum(i.file_size for i in infos)
    if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
        raise ZipExtractError(
            f"Uncompressed contents exceed the {MAX_UNCOMPRESSED_BYTES // (1024 * 1024)}MB limit."
        )

    for info in infos:
        member_path = target / info.filename
        if not _is_within(target, member_path):
            raise ZipExtractError(
                f"Archive entry '{info.filename}' escapes the extraction "
                "directory — rejected as a path-traversal attempt."
            )

    zf.extractall(target)
    return target
