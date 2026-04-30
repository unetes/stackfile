"""Revert a snapshot to a previous state by undoing the last N changes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RevertError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise RevertError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(path: str, data: dict[str, Any]) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def _load_history(history_path: str) -> list[dict[str, Any]]:
    p = Path(history_path)
    if not p.exists():
        return []
    with p.open() as f:
        return json.load(f)


def revert_snapshot(
    snapshot_path: str,
    history_path: str,
    steps: int = 1,
    output: str | None = None,
) -> dict[str, Any]:
    """Revert snapshot to the state it was in `steps` history entries ago."""
    if steps < 1:
        raise RevertError("steps must be >= 1")

    entries = _load_history(history_path)
    if not entries:
        raise RevertError("No history entries found; cannot revert.")

    # Filter entries that reference this snapshot
    relevant = [
        e for e in entries
        if e.get("snapshot_path") == snapshot_path and "state" in e
    ]

    if len(relevant) < steps:
        raise RevertError(
            f"Not enough history to revert {steps} step(s); "
            f"only {len(relevant)} recorded."
        )

    target_entry = relevant[-(steps)]
    reverted = target_entry["state"]

    dest = output or snapshot_path
    _save(dest, reverted)
    return reverted


def revert_and_print(
    snapshot_path: str,
    history_path: str,
    steps: int = 1,
    output: str | None = None,
    as_json: bool = False,
) -> None:
    result = revert_snapshot(snapshot_path, history_path, steps, output)
    dest = output or snapshot_path
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        total = sum(
            len(result.get(sec, {}).get("packages", []))
            for sec in ("pip", "npm", "brew")
        )
        print(f"Reverted {dest} ({steps} step(s) back) — {total} package(s) restored.")
