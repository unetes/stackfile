"""Sort packages within snapshot sections alphabetically or by version."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SortError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise SortError(f"Snapshot file not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def _sort_packages(packages: list[dict], key: str, reverse: bool) -> list[dict]:
    """Sort a list of package dicts by a given key."""
    def _get(pkg: dict) -> Any:
        value = pkg.get(key, "")
        return value.lower() if isinstance(value, str) else value

    return sorted(packages, key=_get, reverse=reverse)


def sort_snapshot(
    input_path: str,
    output_path: str | None = None,
    key: str = "name",
    reverse: bool = False,
    sections: list[str] | None = None,
) -> dict:
    """Sort packages in each section of the snapshot.

    Args:
        input_path: Path to the snapshot JSON file.
        output_path: Where to write the sorted snapshot. Defaults to input_path.
        key: Package field to sort by ('name' or 'version').
        reverse: If True, sort in descending order.
        sections: Limit sorting to these sections. None means all sections.

    Returns:
        The sorted snapshot dict.
    """
    if key not in ("name", "version"):
        raise SortError(f"Invalid sort key '{key}'. Must be 'name' or 'version'.")

    data = _load(input_path)
    target_sections = sections or ["pip", "npm", "brew"]

    for section in target_sections:
        if section in data and isinstance(data[section], list):
            data[section] = _sort_packages(data[section], key=key, reverse=reverse)

    dest = output_path or input_path
    _save(data, dest)
    return data
