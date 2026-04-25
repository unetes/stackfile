"""Archive a snapshot to a timestamped backup file."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


class ArchiveError(Exception):
    pass


def _load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise ArchiveError(f"Snapshot not found: {path}")
    except json.JSONDecodeError as e:
        raise ArchiveError(f"Invalid JSON in {path}: {e}")


def _archive_path(source: str, archive_dir: str) -> Path:
    """Build a timestamped archive path inside archive_dir."""
    stem = Path(source).stem
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = Path(archive_dir) / f"{stem}.{ts}.json"
    return dest


def archive_snapshot(source: str, archive_dir: str = "archives") -> str:
    """Copy *source* snapshot into *archive_dir* with a UTC timestamp suffix.

    Returns the path of the created archive file.
    """
    data = _load(source)  # validate it is a readable snapshot
    dest = _archive_path(source, archive_dir)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return str(dest)


def list_archives(archive_dir: str = "archives", stem: str | None = None) -> list[str]:
    """Return sorted list of archive file paths inside *archive_dir*.

    If *stem* is provided, only archives whose filename starts with that stem
    are returned.
    """
    d = Path(archive_dir)
    if not d.exists():
        return []
    files = sorted(d.glob("*.json"))
    if stem:
        files = [f for f in files if f.name.startswith(stem)]
    return [str(f) for f in files]


def restore_archive(archive_path: str, dest: str) -> None:
    """Restore an archived snapshot to *dest*."""
    _load(archive_path)  # validate
    shutil.copy2(archive_path, dest)
