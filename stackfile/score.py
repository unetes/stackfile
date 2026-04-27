"""score.py — Compute a health/quality score for a snapshot."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ScoreError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ScoreError(f"File not found: {path}")
    with p.open() as f:
        return json.load(f)


def _section_score(packages: list[dict[str, Any]]) -> dict[str, int | float]:
    """Return per-section scoring metrics."""
    total = len(packages)
    if total == 0:
        return {"total": 0, "pinned": 0, "versioned": 0, "annotated": 0, "score": 100}

    pinned = sum(1 for p in packages if p.get("pinned"))
    versioned = sum(1 for p in packages if p.get("version") and p["version"] not in ("", "*", "latest"))
    annotated = sum(1 for p in packages if p.get("note"))

    # Score: 50 pts for versioned ratio, 30 for pinned ratio, 20 for annotated ratio
    score = round(
        50 * (versioned / total)
        + 30 * (pinned / total)
        + 20 * (annotated / total)
    )
    return {
        "total": total,
        "pinned": pinned,
        "versioned": versioned,
        "annotated": annotated,
        "score": score,
    }


def score_snapshot(path: str) -> dict[str, Any]:
    """Return a full score report for the snapshot at *path*."""
    data = _load(path)
    sections = ["pip", "npm", "brew"]
    report: dict[str, Any] = {"sections": {}}

    total_packages = 0
    weighted_sum = 0

    for section in sections:
        packages = data.get(section, [])
        if not isinstance(packages, list):
            packages = []
        metrics = _section_score(packages)
        report["sections"][section] = metrics
        total_packages += metrics["total"]
        weighted_sum += metrics["score"] * metrics["total"]

    overall = round(weighted_sum / total_packages) if total_packages else 100
    report["overall"] = overall
    report["total_packages"] = total_packages
    report["grade"] = _grade(overall)
    return report


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def format_score(report: dict[str, Any]) -> str:
    lines = [f"Overall score: {report['overall']}/100  (Grade: {report['grade']})",
             f"Total packages: {report['total_packages']}", ""]
    for section, m in report["sections"].items():
        lines.append(f"  [{section}]  total={m['total']}  versioned={m['versioned']}  "
                     f"pinned={m['pinned']}  annotated={m['annotated']}  score={m['score']}")
    return "\n".join(lines)


def score_and_print(path: str, as_json: bool = False) -> None:
    report = score_snapshot(path)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(format_score(report))
