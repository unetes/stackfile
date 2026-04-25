"""Mark packages in a snapshot with a custom status flag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class MarkError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise MarkError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def mark_package(
    data: dict,
    name: str,
    status: str,
    section: Optional[str] = None,
) -> int:
    """Set a 'status' field on matching packages. Returns count of updated packages."""
    sections = [section] if section else ["pip", "npm", "brew"]
    updated = 0
    for sec in sections:
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        for pkg in packages:
            if isinstance(pkg, dict) and pkg.get("name", "").lower() == name.lower():
                pkg["status"] = status
                updated += 1
    return updated


def unmark_package(
    data: dict,
    name: str,
    section: Optional[str] = None,
) -> int:
    """Remove the 'status' field from matching packages. Returns count of updated packages."""
    sections = [section] if section else ["pip", "npm", "brew"]
    updated = 0
    for sec in sections:
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        for pkg in packages:
            if isinstance(pkg, dict) and pkg.get("name", "").lower() == name.lower():
                if "status" in pkg:
                    del pkg["status"]
                    updated += 1
    return updated


def mark_and_save(
    input_path: str,
    name: str,
    status: str,
    output_path: Optional[str] = None,
    section: Optional[str] = None,
) -> int:
    data = _load(input_path)
    count = mark_package(data, name, status, section=section)
    _save(data, output_path or input_path)
    return count
