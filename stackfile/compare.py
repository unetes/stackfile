"""Compare two snapshots and produce a similarity report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CompareError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise CompareError(f"Cannot load snapshot '{path}': {exc}") from exc


def _section_packages(snapshot: dict[str, Any], section: str) -> dict[str, str]:
    """Return {name: version} for a given section."""
    packages = snapshot.get(section, {}).get("packages", [])
    return {p["name"]: p["version"] for p in packages if "name" in p}


def compare_snapshots(
    path_a: str, path_b: str, sections: list[str] | None = None
) -> dict[str, Any]:
    """Return a comparison report between two snapshots."""
    snap_a = _load(path_a)
    snap_b = _load(path_b)

    all_sections = sections or ["pip", "npm", "brew"]
    report: dict[str, Any] = {
        "snapshot_a": path_a,
        "snapshot_b": path_b,
        "sections": {},
    }

    total_union = 0
    total_common = 0

    for section in all_sections:
        pkgs_a = _section_packages(snap_a, section)
        pkgs_b = _section_packages(snap_b, section)

        names_a = set(pkgs_a)
        names_b = set(pkgs_b)
        common_names = names_a & names_b

        same = {n for n in common_names if pkgs_a[n] == pkgs_b[n]}
        version_diff = {n for n in common_names if pkgs_a[n] != pkgs_b[n]}
        only_a = names_a - names_b
        only_b = names_b - names_a

        union = len(names_a | names_b)
        similarity = round(len(same) / union * 100, 1) if union else 100.0

        report["sections"][section] = {
            "only_in_a": sorted(only_a),
            "only_in_b": sorted(only_b),
            "version_diff": sorted(version_diff),
            "identical": sorted(same),
            "similarity_pct": similarity,
        }

        total_union += union
        total_common += len(same)

    overall = round(total_common / total_union * 100, 1) if total_union else 100.0
    report["overall_similarity_pct"] = overall
    return report


def format_compare(report: dict[str, Any]) -> str:
    """Return a human-readable comparison summary."""
    lines = [
        f"Comparing: {report['snapshot_a']}  vs  {report['snapshot_b']}",
        f"Overall similarity: {report['overall_similarity_pct']}%",
        "",
    ]
    for section, data in report["sections"].items():
        lines.append(f"[{section}]  similarity: {data['similarity_pct']}%")
        if data["only_in_a"]:
            lines.append(f"  Only in A : {', '.join(data['only_in_a'])}")
        if data["only_in_b"]:
            lines.append(f"  Only in B : {', '.join(data['only_in_b'])}")
        if data["version_diff"]:
            lines.append(f"  Ver diff  : {', '.join(data['version_diff'])}")
        if not (data["only_in_a"] or data["only_in_b"] or data["version_diff"]):
            lines.append("  Identical")
        lines.append("")
    return "\n".join(lines).rstrip()
