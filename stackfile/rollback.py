"""Rollback a snapshot file to a previous state recorded in history."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from stackfile.history import _load_history, HistoryError


class RollbackError(Exception):
    pass


def _load_history_entries(history_file: Path) -> list[dict]:
    try:
        return _load_history(history_file)
    except HistoryError as exc:
        raise RollbackError(str(exc)) from exc


def list_rollback_points(history_file: Path) -> list[dict]:
    """Return history entries that have a saved snapshot path."""
    entries = _load_history_entries(history_file)
    return [e for e in entries if e.get("snapshot_path")]


def rollback_to(index: int, history_file: Path, output: Optional[Path] = None) -> Path:
    """Restore snapshot to the state recorded at *index* in history.

    index 0 is the most recent entry.
    Returns the path that was written.
    """
    points = list_rollback_points(history_file)
    if not points:
        raise RollbackError("No rollback points found in history.")
    if index < 0 or index >= len(points):
        raise RollbackError(
            f"Index {index} out of range (0–{len(points) - 1})."
        )

    entry = points[index]
    src = Path(entry["snapshot_path"])
    if not src.exists():
        raise RollbackError(f"Snapshot file not found: {src}")

    dest = output or src
    shutil.copy2(src, dest)
    return dest


def rollback_and_print(
    index: int,
    history_file: Path,
    output: Optional[Path] = None,
    as_json: bool = False,
) -> None:
    dest = rollback_to(index, history_file, output)
    if as_json:
        print(json.dumps({"restored": str(dest), "index": index}))
    else:
        print(f"Rolled back to history index {index} → {dest}")
