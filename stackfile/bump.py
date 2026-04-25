"""Bump package versions in a snapshot by a semver component."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

BumpLevel = Literal["major", "minor", "patch"]


class BumpError(Exception):
    pass


def _load(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise BumpError(f"Snapshot not found: {path}")
    except json.JSONDecodeError as exc:
        raise BumpError(f"Invalid JSON in {path}: {exc}") from exc


def _save(data: dict, path: str) -> None:
    Path(path).write_text(json.dumps(data, indent=2))


def _bump_version(version: str, level: BumpLevel) -> str | None:
    """Return bumped version string, or None if version cannot be parsed."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(.*)", version.lstrip("^~="))
    if not match:
        return None
    major, minor, patch, rest = int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4)
    if level == "major":
        return f"{major + 1}.0.0{rest}"
    if level == "minor":
        return f"{major}.{minor + 1}.0{rest}"
    return f"{major}.{minor}.{patch + 1}{rest}"


def _bump_packages(packages: list[dict], level: BumpLevel, name: str | None) -> int:
    """Bump packages in-place; return count of bumped entries."""
    count = 0
    for pkg in packages:
        if name and pkg.get("name") != name:
            continue
        version = pkg.get("version", "")
        bumped = _bump_version(str(version), level)
        if bumped is not None:
            pkg["version"] = bumped
            count += 1
    return count


def bump_snapshot(
    input_path: str,
    level: BumpLevel,
    *,
    name: str | None = None,
    section: str | None = None,
    output_path: str | None = None,
) -> dict:
    """Bump semver versions in *input_path* and return updated snapshot."""
    data = _load(input_path)
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in data:
            raise BumpError(f"Section '{section}' not found in snapshot")
        sections = [section]

    total = 0
    for sec in sections:
        pkgs = data.get(sec, [])
        if isinstance(pkgs, list):
            total += _bump_packages(pkgs, level, name)

    out = output_path or input_path
    _save(data, out)
    data["_bumped"] = total
    return data
