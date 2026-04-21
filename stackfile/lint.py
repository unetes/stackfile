"""Lint a snapshot file for common issues and best practices."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


class LintError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise LintError(f"Cannot read snapshot: {exc}") from exc


def lint_snapshot(data: dict[str, Any]) -> list[str]:
    """Return a list of warning strings for the given snapshot data."""
    warnings: list[str] = []

    for section in ("pip", "npm", "brew"):
        packages = data.get(section, [])
        if not isinstance(packages, list):
            continue
        for pkg in packages:
            name = pkg.get("name", "") if isinstance(pkg, dict) else str(pkg)
            version = pkg.get("version", "") if isinstance(pkg, dict) else ""

            if not version or version in ("latest", "*", ""):
                warnings.append(
                    f"[{section}] '{name}' has no pinned version — consider pinning."
                )

            if isinstance(pkg, dict) and pkg.get("pinned") is False:
                warnings.append(
                    f"[{section}] '{name}' is explicitly marked as unpinned."
                )

    tags = data.get("tags", [])
    if isinstance(tags, list) and len(tags) == 0:
        warnings.append("Snapshot has no tags — consider adding environment tags.")

    created_at = data.get("created_at", "")
    if not created_at:
        warnings.append("Snapshot is missing 'created_at' timestamp.")

    return warnings


def format_lint_results(warnings: list[str]) -> str:
    if not warnings:
        return "No lint warnings found."
    lines = [f"  - {w}" for w in warnings]
    return "Lint warnings:\n" + "\n".join(lines)


def lint_and_print(path: str, as_json: bool = False) -> int:
    try:
        data = _load(path)
    except LintError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    warnings = lint_snapshot(data)

    if as_json:
        print(json.dumps({"warnings": warnings, "count": len(warnings)}, indent=2))
    else:
        print(format_lint_results(warnings))

    return 0
