"""Mask sensitive package names or versions in a snapshot."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional


class MaskError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise MaskError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _mask_value(value: str, char: str = "*", keep: int = 0) -> str:
    """Replace most characters in *value* with *char*, optionally keeping
    the last *keep* characters visible."""
    if not value or not isinstance(value, str):
        return value
    if keep and len(value) > keep:
        return char * (len(value) - keep) + value[-keep:]
    return char * len(value)


def mask_snapshot(
    data: dict,
    *,
    pattern: Optional[str] = None,
    section: Optional[str] = None,
    field: str = "version",
    char: str = "*",
    keep: int = 0,
) -> tuple[dict, int]:
    """Mask *field* values for packages whose name matches *pattern*.

    Returns the modified snapshot and the count of masked packages.
    """
    import copy

    result = copy.deepcopy(data)
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in sections:
            raise MaskError(f"Unknown section: {section}")
        sections = [section]

    regex = re.compile(pattern, re.IGNORECASE) if pattern else None
    count = 0

    for sec in sections:
        for pkg in result.get(sec, []):
            name = pkg.get("name", "")
            if regex is None or regex.search(name):
                if field in pkg:
                    pkg[field] = _mask_value(str(pkg[field]), char=char, keep=keep)
                    count += 1

    return result, count


def mask_and_save(
    input_path: str,
    output_path: str,
    *,
    pattern: Optional[str] = None,
    section: Optional[str] = None,
    field: str = "version",
    char: str = "*",
    keep: int = 0,
) -> int:
    data = _load(input_path)
    result, count = mask_snapshot(
        data, pattern=pattern, section=section, field=field, char=char, keep=keep
    )
    _save(result, output_path)
    return count
