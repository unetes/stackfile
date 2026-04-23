"""List and display all annotated packages (those with notes) in a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple


class NotesError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise NotesError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def list_notes(data: dict) -> List[Tuple[str, str, str]]:
    """Return list of (section, package_name, note) for all annotated packages."""
    results = []
    for section in ("pip", "npm", "brew"):
        for pkg in data.get(section, []):
            if isinstance(pkg, dict) and pkg.get("note"):
                results.append((section, pkg["name"], pkg["note"]))
    return results


def format_notes(entries: List[Tuple[str, str, str]]) -> str:
    if not entries:
        return "No annotations found."
    lines = []
    for section, name, note in entries:
        lines.append(f"[{section}] {name}: {note}")
    return "\n".join(lines)


def notes_and_print(input_path: str, as_json: bool = False) -> int:
    data = _load(input_path)
    entries = list_notes(data)
    if as_json:
        print(json.dumps([{"section": s, "name": n, "note": t} for s, n, t in entries], indent=2))
    else:
        print(format_notes(entries))
    return 0
