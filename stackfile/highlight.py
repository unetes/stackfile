"""Highlight packages in a snapshot by marking them visually in output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class HighlightError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise HighlightError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _matches(pkg: dict[str, Any], query: str, case_sensitive: bool) -> bool:
    name = pkg.get("name", "")
    if not case_sensitive:
        return query.lower() in name.lower()
    return query in name


def highlight_packages(
    data: dict[str, Any],
    query: str,
    section: str | None = None,
    case_sensitive: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    """Return a mapping of section -> packages that match the query."""
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in sections:
            raise HighlightError(f"Unknown section: {section}")
        sections = [section]

    results: dict[str, list[dict[str, Any]]] = {}
    for sec in sections:
        packages = data.get(sec, [])
        matched = [p for p in packages if _matches(p, query, case_sensitive)]
        if matched:
            results[sec] = matched
    return results


def format_highlight(
    results: dict[str, list[dict[str, Any]]],
    query: str,
    as_json: bool = False,
) -> str:
    if as_json:
        return json.dumps(results, indent=2)

    if not results:
        return f"No packages matching '{query}' found."

    lines: list[str] = []
    for sec, packages in results.items():
        lines.append(f"[{sec}]")
        for pkg in packages:
            version = pkg.get("version", "*")
            note = pkg.get("note", "")
            entry = f"  * {pkg['name']}=={version}"
            if note:
                entry += f"  # {note}"
            lines.append(entry)
    return "\n".join(lines)


def highlight_and_print(
    path: str,
    query: str,
    section: str | None = None,
    case_sensitive: bool = False,
    as_json: bool = False,
) -> int:
    data = _load(path)
    results = highlight_packages(data, query, section=section, case_sensitive=case_sensitive)
    print(format_highlight(results, query, as_json=as_json))
    return 0 if results else 1
