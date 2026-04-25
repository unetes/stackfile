"""trim.py — Remove packages from a snapshot that exceed a count limit per section."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class TrimError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise TrimError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def _trim_packages(packages: list[dict], limit: int, key: str) -> tuple[list[dict], int]:
    """Keep only the first `limit` packages sorted by `key`. Returns (trimmed, removed_count)."""
    if limit <= 0:
        raise TrimError(f"Limit must be a positive integer, got {limit}")
    sorted_pkgs = sorted(packages, key=lambda p: p.get(key, "").lower())
    removed = max(0, len(sorted_pkgs) - limit)
    return sorted_pkgs[:limit], removed


def trim_snapshot(
    input_path: str,
    output_path: Optional[str],
    limit: int,
    section: Optional[str] = None,
    sort_key: str = "name",
) -> dict:
    """Trim packages in each section (or a specific section) to at most `limit` entries."""
    data = _load(input_path)
    sections = ["pip", "npm", "brew"]
    total_removed = 0
    report: dict[str, int] = {}

    for sec in sections:
        if section and sec != section:
            continue
        pkgs = data.get(sec, {}).get("packages", [])
        if not isinstance(pkgs, list):
            continue
        trimmed, removed = _trim_packages(pkgs, limit, sort_key)
        data.setdefault(sec, {})["packages"] = trimmed
        report[sec] = removed
        total_removed += removed

    dest = output_path or input_path
    _save(data, dest)
    return {"removed": total_removed, "by_section": report, "output": dest}
