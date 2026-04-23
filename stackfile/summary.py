"""Generate a human-readable summary of a snapshot file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SummaryError(Exception):
    """Raised when summary generation fails."""


def _load(path: str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise SummaryError(f"Snapshot not found: {path}")
    except json.JSONDecodeError as exc:
        raise SummaryError(f"Invalid JSON in {path}: {exc}")


def summarize_snapshot(data: dict[str, Any]) -> dict[str, Any]:
    """Return a summary dict with counts and metadata for each section."""
    sections = ("pip", "npm", "brew")
    result: dict[str, Any] = {
        "version": data.get("version", "unknown"),
        "created_at": data.get("created_at", "unknown"),
        "tags": data.get("tags", []),
        "description": data.get("description", ""),
        "sections": {},
        "total_packages": 0,
    }

    for section in sections:
        packages = data.get(section, {}).get("packages", [])
        pinned = [p for p in packages if p.get("version") and p["version"] not in ("*", "latest", None)]
        result["sections"][section] = {
            "count": len(packages),
            "pinned": len(pinned),
            "unpinned": len(packages) - len(pinned),
        }
        result["total_packages"] += len(packages)

    return result


def format_summary(summary: dict[str, Any]) -> str:
    """Format a summary dict as a human-readable string."""
    lines = [
        f"Version   : {summary['version']}",
        f"Created   : {summary['created_at']}",
        f"Tags      : {', '.join(summary['tags']) if summary['tags'] else '(none)'}",
        f"Description: {summary['description'] or '(none)'}",
        f"Total pkgs: {summary['total_packages']}",
        "",
        f"  {'Section':<8} {'Total':>6} {'Pinned':>8} {'Unpinned':>10}",
        "  " + "-" * 36,
    ]
    for section, info in summary["sections"].items():
        lines.append(
            f"  {section:<8} {info['count']:>6} {info['pinned']:>8} {info['unpinned']:>10}"
        )
    return "\n".join(lines)


def summarize_and_print(path: str, as_json: bool = False) -> dict[str, Any]:
    """Load snapshot, compute summary, print it, and return the summary dict."""
    data = _load(path)
    summary = summarize_snapshot(data)
    if as_json:
        print(json.dumps(summary, indent=2))
    else:
        print(format_summary(summary))
    return summary
