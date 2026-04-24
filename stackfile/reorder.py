"""Reorder packages within a snapshot section by moving a package to a specific index."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class ReorderError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise ReorderError(f"Snapshot file not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def reorder_package(
    data: dict,
    name: str,
    index: int,
    section: Optional[str] = None,
) -> int:
    """Move *name* to *index* in each matching section (or only *section*).

    Returns the number of sections where the package was moved.
    """
    sections = ["pip", "npm", "brew"]
    if section:
        sections = [section]

    moved = 0
    for sec in sections:
        packages: list = data.get(sec, [])
        matches = [p for p in packages if p.get("name") == name]
        if not matches:
            continue
        pkg = matches[0]
        packages.remove(pkg)
        clamped = max(0, min(index, len(packages)))
        packages.insert(clamped, pkg)
        data[sec] = packages
        moved += 1
    return moved


def reorder_and_save(
    input_path: str,
    name: str,
    index: int,
    section: Optional[str] = None,
    output_path: Optional[str] = None,
) -> int:
    """Load, reorder, and save.  Returns number of sections affected."""
    data = _load(input_path)
    moved = reorder_package(data, name, index, section=section)
    dest = output_path or input_path
    _save(data, dest)
    return moved
