"""Group packages in a snapshot under a named label."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class GroupError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise GroupError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_group(data: dict, section: str, package: str, group: str) -> int:
    """Tag *package* in *section* with *group*. Returns number of packages updated."""
    packages = data.get(section, [])
    updated = 0
    for pkg in packages:
        if isinstance(pkg, dict) and pkg.get("name") == package:
            pkg["group"] = group
            updated += 1
    return updated


def remove_group(data: dict, section: str, package: str) -> int:
    """Remove the group label from *package* in *section*. Returns number updated."""
    packages = data.get(section, [])
    updated = 0
    for pkg in packages:
        if isinstance(pkg, dict) and pkg.get("name") == package:
            pkg.pop("group", None)
            updated += 1
    return updated


def list_groups(data: dict) -> dict[str, list[dict]]:
    """Return a mapping of group name -> list of {section, name} entries."""
    groups: dict[str, list[dict]] = {}
    for section in ("pip", "npm", "brew"):
        for pkg in data.get(section, []):
            if isinstance(pkg, dict) and "group" in pkg:
                g = pkg["group"]
                groups.setdefault(g, []).append({"section": section, "name": pkg.get("name", "")})
    return groups


def group_and_save(
    input_path: str,
    section: str,
    package: str,
    group: Optional[str],
    output_path: Optional[str] = None,
) -> int:
    data = _load(input_path)
    if group is None:
        count = remove_group(data, section, package)
    else:
        count = add_group(data, section, package, group)
    _save(data, output_path or input_path)
    return count
