"""Promote a package from one section to another in a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class PromoteError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise PromoteError(f"Snapshot file not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def promote_package(
    data: dict,
    name: str,
    from_section: str,
    to_section: str,
    overwrite: bool = False,
) -> int:
    """Move a package entry from one section to another.

    Returns the number of packages moved (0 or 1).
    """
    src = data.get(from_section)
    if not isinstance(src, list):
        raise PromoteError(f"Section '{from_section}' not found or not a list.")

    dst = data.get(to_section)
    if not isinstance(dst, list):
        raise PromoteError(f"Section '{to_section}' not found or not a list.")

    # Find the package in the source section
    match = next((p for p in src if p.get("name") == name), None)
    if match is None:
        return 0

    # Check for conflict in destination
    existing = next((p for p in dst if p.get("name") == name), None)
    if existing is not None:
        if not overwrite:
            raise PromoteError(
                f"Package '{name}' already exists in '{to_section}'. "
                "Use overwrite=True to replace it."
            )
        dst.remove(existing)

    src.remove(match)
    dst.append(match)
    return 1


def promote_and_save(
    input_path: str,
    name: str,
    from_section: str,
    to_section: str,
    output_path: Optional[str] = None,
    overwrite: bool = False,
) -> int:
    data = _load(input_path)
    moved = promote_package(data, name, from_section, to_section, overwrite=overwrite)
    _save(data, output_path or input_path)
    return moved
