"""Diff two stackfile snapshots and report differences."""

import json
from pathlib import Path
from typing import Any


def _load(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def _diff_section(old: dict, new: dict, section: str) -> dict[str, list[str]]:
    old_pkgs = {p["name"]: p["version"] for p in old.get(section, [])}
    new_pkgs = {p["name"]: p["version"] for p in new.get(section, [])}

    added = [
        f"{name}=={ver}" for name, ver in new_pkgs.items() if name not in old_pkgs
    ]
    removed = [
        f"{name}=={ver}" for name, ver in old_pkgs.items() if name not in new_pkgs
    ]
    changed = [
        f"{name}: {old_pkgs[name]} -> {new_pkgs[name]}"
        for name in old_pkgs
        if name in new_pkgs and old_pkgs[name] != new_pkgs[name]
    ]
    return {"added": added, "removed": removed, "changed": changed}


def diff_snapshots(old_path: str, new_path: str) -> dict[str, Any]:
    """Return a structured diff between two snapshot files."""
    old = _load(old_path)
    new = _load(new_path)

    result: dict[str, Any] = {}
    for section in ("pip", "npm", "brew"):
        section_diff = _diff_section(old, new, section)
        if any(section_diff.values()):
            result[section] = section_diff
    return result


def format_diff(diff: dict[str, Any]) -> str:
    """Return a human-readable string of the diff."""
    if not diff:
        return "No differences found."

    lines = []
    for section, changes in diff.items():
        lines.append(f"[{section}]")
        for entry in changes.get("added", []):
            lines.append(f"  + {entry}")
        for entry in changes.get("removed", []):
            lines.append(f"  - {entry}")
        for entry in changes.get("changed", []):
            lines.append(f"  ~ {entry}")
    return "\n".join(lines)
