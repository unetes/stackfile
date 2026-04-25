"""Unlock pinned packages in a snapshot, resetting versions to '*'."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class UnlockError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise UnlockError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _unlock_packages(
    packages: list[dict],
    section: Optional[str],
    current_section: str,
) -> tuple[list[dict], int]:
    """Return updated packages list and count of unlocked entries."""
    if section and section != current_section:
        return packages, 0

    unlocked = 0
    result = []
    for pkg in packages:
        if pkg.get("pinned"):
            pkg = {**pkg, "version": "*", "pinned": False}
            unlocked += 1
        result.append(pkg)
    return result, unlocked


def unlock_snapshot(
    input_path: str,
    output_path: Optional[str] = None,
    section: Optional[str] = None,
) -> int:
    """Unlock all pinned packages in a snapshot.

    Returns the total number of packages unlocked.
    """
    data = _load(input_path)
    total = 0

    for sec in ("pip", "npm", "brew"):
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        updated, count = _unlock_packages(packages, section, sec)
        data[sec] = updated
        total += count

    dest = output_path or input_path
    _save(data, dest)
    return total
