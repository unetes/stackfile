"""Merge two snapshots, with the second taking precedence."""

import json
from pathlib import Path
from datetime import datetime, timezone


def _load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def merge_snapshots(base_path: str, override_path: str) -> dict:
    """Merge two snapshot files. Override packages win on conflict."""
    base = _load(base_path)
    override = _load(override_path)

    merged = {
        "version": base.get("version", 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "packages": {},
    }

    sections = set(list(base.get("packages", {}).keys()) + list(override.get("packages", {}).keys()))

    for section in sections:
        base_pkgs = {p["name"]: p for p in base.get("packages", {}).get(section, [])}
        override_pkgs = {p["name"]: p for p in override.get("packages", {}).get(section, [])}
        merged_pkgs = {**base_pkgs, **override_pkgs}
        merged["packages"][section] = list(merged_pkgs.values())

    return merged


def save_merged(merged: dict, output_path: str) -> None:
    with open(output_path, "w") as f:
        json.dump(merged, f, indent=2)


def merge_and_save(base_path: str, override_path: str, output_path: str) -> dict:
    merged = merge_snapshots(base_path, override_path)
    save_merged(merged, output_path)
    return merged
