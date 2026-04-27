"""Normalize package names and versions in a snapshot."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class NormalizeError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise NormalizeError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _normalize_name(name: str) -> str:
    """Lowercase and replace underscores/dots with hyphens."""
    return re.sub(r"[_\.]+", "-", name.strip().lower())


def _normalize_version(version: str) -> str:
    """Strip leading 'v' or '=' from version strings."""
    return re.sub(r"^[v=]+", "", version.strip())


def _normalize_packages(packages: list[dict]) -> tuple[list[dict], int]:
    changed = 0
    result = []
    for pkg in packages:
        original_name = pkg.get("name", "")
        original_version = pkg.get("version", "")
        new_name = _normalize_name(original_name)
        new_version = _normalize_version(original_version)
        if new_name != original_name or new_version != original_version:
            changed += 1
        result.append({**pkg, "name": new_name, "version": new_version})
    return result, changed


def normalize_snapshot(
    input_path: str,
    output_path: str | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    data = _load(input_path)
    sections = ["pip", "npm", "brew"]
    total_changed = 0

    for sec in sections:
        if section and sec != section:
            continue
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        normalized, changed = _normalize_packages(packages)
        data[sec] = normalized
        total_changed += changed

    dest = output_path or input_path
    _save(data, dest)
    return {"changed": total_changed, "output": dest}
