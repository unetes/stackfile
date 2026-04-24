"""Strip metadata fields from a snapshot, producing a leaner file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_STRIP_FIELDS = ("created_at", "pinned", "cloned_from", "tags", "description")


class StripError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise StripError(f"File not found: {path}")
    with p.open() as fh:
        return json.load(fh)


def _save(data: dict[str, Any], path: str) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def strip_snapshot(
    data: dict[str, Any],
    fields: tuple[str, ...] | list[str] = DEFAULT_STRIP_FIELDS,
    strip_notes: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    """Return a copy of *data* with *fields* removed from the top level.

    If *strip_notes* is True, also remove the ``note`` key from every
    package entry in every section.

    Returns the cleaned snapshot and a list of field names that were
    actually removed.
    """
    result = dict(data)
    removed: list[str] = []

    for field in fields:
        if field in result:
            del result[field]
            removed.append(field)

    if strip_notes:
        for section in ("pip", "npm", "brew"):
            packages = result.get(section, [])
            if isinstance(packages, list):
                result[section] = [
                    {k: v for k, v in pkg.items() if k != "note"}
                    if isinstance(pkg, dict)
                    else pkg
                    for pkg in packages
                ]

    return result, removed


def strip_and_save(
    input_path: str,
    output_path: str | None = None,
    fields: tuple[str, ...] | list[str] = DEFAULT_STRIP_FIELDS,
    strip_notes: bool = False,
) -> list[str]:
    """Load *input_path*, strip fields, write to *output_path* (or overwrite)."""
    data = _load(input_path)
    cleaned, removed = strip_snapshot(data, fields=fields, strip_notes=strip_notes)
    _save(cleaned, output_path or input_path)
    return removed
