"""Apply a partial update (patch) to a snapshot file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class PatchError(Exception):
    pass


def _load(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise PatchError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: Dict[str, Any], path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _patch_packages(
    packages: List[Dict[str, Any]],
    updates: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], int]:
    """Apply version updates to matching packages. Returns updated list and count."""
    index = {pkg["name"]: i for i, pkg in enumerate(packages)}
    count = 0
    result = [p.copy() for p in packages]
    for update in updates:
        name = update.get("name")
        if name and name in index:
            result[index[name]].update({k: v for k, v in update.items() if k != "name"})
            count += 1
    return result, count


def patch_snapshot(
    input_path: str,
    patches: Dict[str, List[Dict[str, Any]]],
    output_path: Optional[str] = None,
    section: Optional[str] = None,
) -> Dict[str, Any]:
    """Patch package entries in the snapshot.

    Args:
        input_path: Path to the source snapshot JSON.
        patches: Mapping of section name to list of package patch dicts.
        output_path: Destination path; defaults to input_path.
        section: If set, restrict patching to this section only.

    Returns:
        The updated snapshot dict.
    """
    data = _load(input_path)
    sections = ["pip", "npm", "brew"]
    total = 0

    for sec in sections:
        if section and sec != section:
            continue
        if sec not in patches:
            continue
        existing = data.get(sec, {}).get("packages", [])
        updated, count = _patch_packages(existing, patches[sec])
        if sec not in data:
            data[sec] = {}
        data[sec]["packages"] = updated
        total += count

    dest = output_path or input_path
    _save(data, dest)
    return data
