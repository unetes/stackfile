"""Inspect a snapshot: show detailed info about a single package."""

import json
from pathlib import Path
from typing import Optional


class InspectError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise InspectError(f"Snapshot not found: {path}")
    with open(p) as f:
        return json.load(f)


def inspect_package(snapshot: dict, name: str, section: Optional[str] = None) -> list[dict]:
    """Return all matching package entries across sections (or a specific section)."""
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in snapshot:
            raise InspectError(f"Section '{section}' not found in snapshot")
        sections = [section]

    results = []
    for sec in sections:
        for pkg in snapshot.get(sec, []):
            pkg_name = pkg.get("name", "")
            if pkg_name.lower() == name.lower():
                results.append({"section": sec, **pkg})
    return results


def format_inspect(results: list[dict], fmt: str = "human") -> str:
    if fmt == "json":
        return json.dumps(results, indent=2)
    if not results:
        return "Package not found."
    lines = []
    for entry in results:
        lines.append(f"[{entry['section']}] {entry.get('name')}")
        for k, v in entry.items():
            if k in ("section", "name"):
                continue
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def inspect_and_print(path: str, name: str, section: Optional[str] = None, fmt: str = "human") -> int:
    try:
        snapshot = _load(path)
        results = inspect_package(snapshot, name, section=section)
        print(format_inspect(results, fmt=fmt))
        return 0
    except InspectError as e:
        print(f"Error: {e}")
        return 1
