"""Add, update, or remove inline notes/annotations on packages in a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class AnnotateError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise AnnotateError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def annotate_package(
    data: dict,
    package: str,
    note: Optional[str],
    section: Optional[str] = None,
) -> int:
    """Set or clear the 'note' field on matching packages. Returns count of updates."""
    sections = [section] if section else ["pip", "npm", "brew"]
    updated = 0
    for sec in sections:
        for pkg in data.get(sec, []):
            if isinstance(pkg, dict) and pkg.get("name") == package:
                if note is None:
                    pkg.pop("note", None)
                else:
                    pkg["note"] = note
                updated += 1
    return updated


def annotate_and_save(
    input_path: str,
    package: str,
    note: Optional[str],
    output_path: Optional[str] = None,
    section: Optional[str] = None,
) -> int:
    data = _load(input_path)
    count = annotate_package(data, package, note, section=section)
    _save(data, output_path or input_path)
    return count
