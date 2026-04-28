"""stackfile.status — Show a concise health/status overview of a snapshot file.

Reports counts, pinned ratio, lint warnings, audit freshness, and score grade
in a single glanceable summary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StatusError(Exception):
    """Raised when status cannot be computed."""


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise StatusError(f"Snapshot not found: {path}")
    with p.open() as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_packages(snapshot: dict[str, Any]) -> dict[str, int]:
    """Return per-section package counts."""
    counts: dict[str, int] = {}
    for section in ("pip", "npm", "brew"):
        pkgs = snapshot.get(section, {}).get("packages", [])
        counts[section] = len(pkgs) if isinstance(pkgs, list) else 0
    return counts


def _pinned_ratio(snapshot: dict[str, Any]) -> tuple[int, int]:
    """Return (pinned_count, total_count) across all sections."""
    pinned = 0
    total = 0
    for section in ("pip", "npm", "brew"):
        pkgs = snapshot.get(section, {}).get("packages", [])
        if not isinstance(pkgs, list):
            continue
        for pkg in pkgs:
            total += 1
            ver = pkg.get("version", "")
            if ver and ver not in ("*", "latest", ""):
                pinned += 1
    return pinned, total


def _lint_warning_count(snapshot: dict[str, Any]) -> int:
    """Count lint-style warnings without importing the full lint module."""
    warnings = 0
    for section in ("pip", "npm", "brew"):
        pkgs = snapshot.get(section, {}).get("packages", [])
        if not isinstance(pkgs, list):
            continue
        for pkg in pkgs:
            ver = pkg.get("version", "")
            if not ver:
                warnings += 1
            elif ver in ("*", "latest"):
                warnings += 1
    return warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def status_snapshot(path: str) -> dict[str, Any]:
    """Compute status information for *path* and return a structured dict."""
    snapshot = _load(path)

    counts = _count_packages(snapshot)
    total = sum(counts.values())
    pinned, pin_total = _pinned_ratio(snapshot)
    pin_pct = round(100 * pinned / pin_total) if pin_total else 0
    lint_warnings = _lint_warning_count(snapshot)

    # Simple grade derived from pinned percentage and lint warnings
    if pin_pct >= 90 and lint_warnings == 0:
        grade = "A"
    elif pin_pct >= 70 and lint_warnings <= 2:
        grade = "B"
    elif pin_pct >= 50 and lint_warnings <= 5:
        grade = "C"
    else:
        grade = "D"

    return {
        "path": path,
        "version": snapshot.get("version", "unknown"),
        "created_at": snapshot.get("created_at", ""),
        "total_packages": total,
        "sections": counts,
        "pinned": pinned,
        "pinned_pct": pin_pct,
        "lint_warnings": lint_warnings,
        "grade": grade,
        "tags": snapshot.get("tags", []),
    }


def format_status(result: dict[str, Any], *, as_json: bool = False) -> str:
    """Format *result* for terminal output."""
    if as_json:
        return json.dumps(result, indent=2)

    lines = [
        f"Snapshot : {result['path']}",
        f"Version  : {result['version']}",
        f"Created  : {result['created_at'] or 'n/a'}",
        "",
        "Packages",
        f"  pip  : {result['sections'].get('pip', 0)}",
        f"  npm  : {result['sections'].get('npm', 0)}",
        f"  brew : {result['sections'].get('brew', 0)}",
        f"  total: {result['total_packages']}",
        "",
        f"Pinned   : {result['pinned']}/{result['total_packages']} ({result['pinned_pct']}%)",
        f"Warnings : {result['lint_warnings']}",
        f"Grade    : {result['grade']}",
    ]
    if result["tags"]:
        lines.append(f"Tags     : {', '.join(result['tags'])}")
    return "\n".join(lines)


def status_and_print(path: str, *, as_json: bool = False) -> None:
    """Print the status of *path* to stdout."""
    result = status_snapshot(path)
    print(format_status(result, as_json=as_json))
