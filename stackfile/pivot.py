"""pivot.py – reorganise a snapshot by grouping packages under their group labels."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PivotError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise PivotError(f"File not found: {path}")
    with p.open() as fh:
        return json.load(fh)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as fh:
        json.dump(data, fh, indent=2)


def pivot_snapshot(data: dict, section: str | None = None) -> dict[str, list[dict]]:
    """Return a mapping of group-label -> [package, ...] across all (or one) section.

    Packages without a group label are placed under the key ``"(ungrouped)"``.
    """
    sections = ["pip", "npm", "brew"]
    if section:
        if section not in sections:
            raise PivotError(f"Unknown section '{section}'. Choose from: {', '.join(sections)}")
        sections = [section]

    result: dict[str, list[dict]] = {}
    for sec in sections:
        for pkg in data.get(sec, []):
            label = pkg.get("group") or "(ungrouped)"
            entry = {"section": sec, **pkg}
            result.setdefault(label, []).append(entry)

    return result


def format_pivot(grouped: dict[str, list[dict]], fmt: str = "human") -> str:
    if fmt == "json":
        return json.dumps(grouped, indent=2)

    if not grouped:
        return "No packages found."

    lines: list[str] = []
    for label in sorted(grouped):
        lines.append(f"[{label}]")
        for pkg in grouped[label]:
            name = pkg.get("name", "?")
            version = pkg.get("version", "")
            sec = pkg.get("section", "")
            version_str = f"=={version}" if version else ""
            lines.append(f"  {name}{version_str}  ({sec})")
    return "\n".join(lines)


def pivot_and_print(
    input_path: str,
    section: str | None = None,
    fmt: str = "human",
    output_path: str | None = None,
) -> int:
    data = _load(input_path)
    grouped = pivot_snapshot(data, section=section)
    output = format_pivot(grouped, fmt=fmt)
    print(output)
    if output_path:
        _save(grouped, output_path)
    return 0
