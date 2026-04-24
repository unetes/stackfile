"""Filter packages in a snapshot by criteria such as section, version pattern, or group label."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class FilterError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FilterError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def _matches(pkg: dict[str, Any], name_pattern: str | None, group: str | None, version_pattern: str | None) -> bool:
    if name_pattern and not re.search(name_pattern, pkg.get("name", ""), re.IGNORECASE):
        return False
    if group and pkg.get("group") != group:
        return False
    if version_pattern and not re.search(version_pattern, pkg.get("version", ""), re.IGNORECASE):
        return False
    return True


def filter_snapshot(
    data: dict,
    sections: list[str] | None = None,
    name_pattern: str | None = None,
    group: str | None = None,
    version_pattern: str | None = None,
) -> dict:
    """Return a copy of *data* containing only packages that match all given criteria."""
    result = {k: v for k, v in data.items() if k not in ("pip", "npm", "brew")}
    all_sections = ["pip", "npm", "brew"]
    target_sections = sections if sections else all_sections

    for section in all_sections:
        pkgs = data.get(section, [])
        if section in target_sections:
            result[section] = [
                p for p in pkgs if _matches(p, name_pattern, group, version_pattern)
            ]
        else:
            result[section] = pkgs
    return result


def filter_and_save(
    input_path: str,
    output_path: str,
    sections: list[str] | None = None,
    name_pattern: str | None = None,
    group: str | None = None,
    version_pattern: str | None = None,
) -> dict:
    data = _load(input_path)
    filtered = filter_snapshot(data, sections=sections, name_pattern=name_pattern, group=group, version_pattern=version_pattern)
    _save(filtered, output_path)
    return filtered
