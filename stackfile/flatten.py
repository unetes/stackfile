"""Flatten a snapshot into a single unified package list across all sections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FlattenError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FlattenError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict[str, Any], path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def flatten_snapshot(
    data: dict[str, Any],
    *,
    include_section: bool = True,
    section: str | None = None,
) -> list[dict[str, Any]]:
    """Return a flat list of package dicts, optionally tagged with their section."""
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in sections:
            raise FlattenError(f"Unknown section: {section!r}")
        sections = [section]

    result: list[dict[str, Any]] = []
    for sec in sections:
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        for pkg in packages:
            entry = dict(pkg)
            if include_section:
                entry["section"] = sec
            result.append(entry)
    return result


def format_flat(packages: list[dict[str, Any]], *, as_json: bool = False) -> str:
    if as_json:
        return json.dumps(packages, indent=2)
    if not packages:
        return "No packages found."
    lines = []
    for pkg in packages:
        sec = pkg.get("section", "")
        name = pkg.get("name", "?")
        version = pkg.get("version", "")
        label = f"[{sec}] " if sec else ""
        version_str = f"=={version}" if version else ""
        lines.append(f"{label}{name}{version_str}")
    return "\n".join(lines)


def flatten_and_print(
    path: str,
    *,
    as_json: bool = False,
    include_section: bool = True,
    section: str | None = None,
) -> list[dict[str, Any]]:
    data = _load(path)
    packages = flatten_snapshot(data, include_section=include_section, section=section)
    print(format_flat(packages, as_json=as_json))
    return packages
