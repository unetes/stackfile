"""compact.py — Remove packages with no version, no group, and no note from a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CompactError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CompactError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _is_empty_package(pkg: dict) -> bool:
    """Return True if the package has no meaningful metadata."""
    has_version = bool(pkg.get("version", "").strip())
    has_group = bool(pkg.get("group", "").strip())
    has_note = bool(pkg.get("note", "").strip())
    return not (has_version or has_group or has_note)


def compact_snapshot(
    data: dict,
    section: str | None = None,
    dry_run: bool = False,
) -> tuple[dict, int]:
    """Remove bare packages (no version, group, or note).

    Returns the compacted snapshot and the number of packages removed.
    """
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in sections:
            raise CompactError(f"Unknown section: {section}")
        sections = [section]

    result = {k: v for k, v in data.items() if k not in ("pip", "npm", "brew")}
    removed = 0

    for sec in ("pip", "npm", "brew"):
        pkgs: list[dict] = data.get(sec, [])
        if sec in sections:
            kept = [p for p in pkgs if not _is_empty_package(p)]
            removed += len(pkgs) - len(kept)
            result[sec] = kept
        else:
            result[sec] = pkgs

    return result, removed


def compact_and_save(
    input_path: str,
    output_path: str | None = None,
    section: str | None = None,
    dry_run: bool = False,
) -> int:
    data = _load(input_path)
    compacted, removed = compact_snapshot(data, section=section, dry_run=dry_run)
    if not dry_run:
        _save(compacted, output_path or input_path)
    return removed
