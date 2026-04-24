"""Deduplicate packages within a snapshot, keeping the last occurrence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DedupeError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise DedupeError(f"File not found: {path}")
    with open(p) as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _dedupe_packages(packages: list[dict]) -> tuple[list[dict], int]:
    """Return (deduped_list, removed_count). Last occurrence wins."""
    seen: dict[str, int] = {}
    for i, pkg in enumerate(packages):
        name = pkg.get("name", "")
        if name:
            seen[name] = i
    deduped = [packages[i] for i in sorted(seen.values())]
    removed = len(packages) - len(deduped)
    return deduped, removed


def dedupe_snapshot(
    input_path: str,
    output_path: str | None = None,
    sections: list[str] | None = None,
) -> dict[str, Any]:
    """Deduplicate packages in snapshot sections.

    Returns a report: {section: removed_count, ...}
    """
    data = _load(input_path)
    target_sections = sections or ["pip", "npm", "brew"]
    report: dict[str, Any] = {}

    for section in target_sections:
        pkgs = data.get(section, {}).get("packages", [])
        if not isinstance(pkgs, list):
            continue
        deduped, removed = _dedupe_packages(pkgs)
        data[section]["packages"] = deduped
        report[section] = removed

    dest = output_path or input_path
    _save(data, dest)
    return report
