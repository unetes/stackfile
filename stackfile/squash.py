"""squash.py — merge multiple snapshot history entries into one consolidated snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SquashError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise SquashError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict[str, Any], path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _merge_packages(
    base: list[dict[str, Any]], override: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Merge two package lists; override wins on name conflict."""
    index: dict[str, dict[str, Any]] = {pkg["name"]: pkg for pkg in base}
    for pkg in override:
        index[pkg["name"]] = pkg
    return list(index.values())


def squash_snapshots(
    paths: list[str],
    label: str | None = None,
) -> dict[str, Any]:
    """Load multiple snapshots and squash them into one.

    Later snapshots in *paths* take precedence over earlier ones.
    The ``created_at`` and ``version`` fields are taken from the first snapshot.
    """
    if not paths:
        raise SquashError("At least one snapshot path is required.")

    snapshots = [_load(p) for p in paths]
    base = snapshots[0]

    result: dict[str, Any] = {
        "version": base.get("version", 1),
        "created_at": base.get("created_at", ""),
        "description": label or base.get("description", ""),
        "squashed_from": paths,
        "pip": [],
        "npm": [],
        "brew": [],
    }

    for snap in snapshots:
        for section in ("pip", "npm", "brew"):
            result[section] = _merge_packages(
                result[section], snap.get(section, [])
            )

    return result


def squash_and_save(
    paths: list[str],
    output: str,
    label: str | None = None,
) -> dict[str, Any]:
    data = squash_snapshots(paths, label=label)
    _save(data, output)
    return data
