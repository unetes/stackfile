"""Classify packages in a snapshot by type/category heuristics."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ClassifyError(Exception):
    pass


_PIP_DEV_KEYWORDS = {"pytest", "black", "flake8", "mypy", "isort", "coverage", "tox", "pre-commit", "hypothesis"}
_NPM_DEV_KEYWORDS = {"eslint", "webpack", "babel", "jest", "mocha", "prettier", "typescript", "rollup", "vite"}
_BREW_SYSTEM_KEYWORDS = {"git", "curl", "wget", "openssl", "gcc", "make", "cmake", "pkg-config"}


def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ClassifyError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _classify_package(name: str, section: str) -> str:
    lower = name.lower()
    if section == "pip":
        if any(k in lower for k in _PIP_DEV_KEYWORDS):
            return "dev"
        return "runtime"
    if section == "npm":
        if any(k in lower for k in _NPM_DEV_KEYWORDS):
            return "dev"
        return "runtime"
    if section == "brew":
        if any(k in lower for k in _BREW_SYSTEM_KEYWORDS):
            return "system"
        return "tool"
    return "unknown"


def classify_snapshot(snapshot: dict[str, Any], section: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Return packages annotated with a 'category' field."""
    results: dict[str, list[dict[str, Any]]] = {}
    sections = [section] if section else ["pip", "npm", "brew"]
    for sec in sections:
        packages = snapshot.get(sec, [])
        if not isinstance(packages, list):
            continue
        classified = []
        for pkg in packages:
            entry = dict(pkg)
            entry["category"] = _classify_package(pkg.get("name", ""), sec)
            classified.append(entry)
        results[sec] = classified
    return results


def format_classify(results: dict[str, list[dict[str, Any]]], fmt: str = "human") -> str:
    if fmt == "json":
        return json.dumps(results, indent=2)
    lines = []
    for sec, packages in results.items():
        if not packages:
            continue
        lines.append(f"[{sec}]")
        for pkg in packages:
            lines.append(f"  {pkg['name']}=={pkg.get('version', '*')}  ({pkg['category']})")
    return "\n".join(lines) if lines else "No packages found."


def classify_and_print(path: str, section: str | None = None, fmt: str = "human") -> None:
    snapshot = _load(path)
    results = classify_snapshot(snapshot, section=section)
    print(format_classify(results, fmt=fmt))
