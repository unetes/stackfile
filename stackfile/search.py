"""Search for a package across sections of a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SearchError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise SearchError(f"Snapshot file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SearchError(f"Invalid JSON in snapshot: {exc}")


def search_snapshot(
    snapshot: dict[str, Any],
    query: str,
    *,
    case_sensitive: bool = False,
) -> dict[str, list[dict[str, str]]]:
    """Return a mapping of section -> matching packages for *query*."""
    needle = query if case_sensitive else query.lower()
    results: dict[str, list[dict[str, str]]] = {}

    sections = ("pip", "npm", "brew")
    for section in sections:
        packages: list[dict[str, str]] = snapshot.get(section, [])
        matches = []
        for pkg in packages:
            name = pkg.get("name", "")
            haystack = name if case_sensitive else name.lower()
            if needle in haystack:
                matches.append(pkg)
        if matches:
            results[section] = matches

    return results


def format_search_results(
    results: dict[str, list[dict[str, str]]],
    query: str,
) -> str:
    """Return a human-readable string for *results*."""
    if not results:
        return f"No packages found matching '{query}'."

    lines: list[str] = [f"Search results for '{query}':"]
    for section, packages in results.items():
        lines.append(f"  [{section}]")
        for pkg in packages:
            version = pkg.get("version", "unknown")
            lines.append(f"    {pkg['name']}=={version}")
    return "\n".join(lines)


def search_and_print(path: str, query: str, *, case_sensitive: bool = False) -> int:
    """Load *path*, search for *query*, print results. Returns exit code."""
    try:
        snapshot = _load(path)
    except SearchError as exc:
        print(f"Error: {exc}")
        return 1

    results = search_snapshot(snapshot, query, case_sensitive=case_sensitive)
    print(format_search_results(results, query))
    return 0 if results else 1
