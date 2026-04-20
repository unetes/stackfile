"""Audit a snapshot for outdated or insecure packages."""
from __future__ import annotations

import json
import subprocess
from typing import Any


class AuditError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def _audit_pip(packages: list[dict]) -> list[dict]:
    """Use pip-audit or pip index to flag outdated pip packages."""
    if not packages:
        return []
    names = [p["name"] for p in packages]
    try:
        output = _run(["pip", "index", "versions", *names])
    except Exception:
        return []
    outdated = []
    for pkg in packages:
        if pkg.get("version") and "LATEST" not in pkg.get("version", ""):
            outdated.append({"manager": "pip", "name": pkg["name"], "current": pkg.get("version", "unknown")})
    return outdated


def _audit_npm(packages: list[dict]) -> list[dict]:
    """Run npm outdated to find packages needing updates."""
    if not packages:
        return []
    try:
        raw = _run(["npm", "outdated", "--json", "--global"])
        data = json.loads(raw) if raw else {}
    except Exception:
        return []
    results = []
    pkg_names = {p["name"] for p in packages}
    for name, info in data.items():
        if name in pkg_names:
            results.append({
                "manager": "npm",
                "name": name,
                "current": info.get("current", "unknown"),
                "latest": info.get("latest", "unknown"),
            })
    return results


def audit_snapshot(path: str) -> dict[str, list[dict]]:
    """Return audit results keyed by manager."""
    data = _load(path)
    results: dict[str, list[dict]] = {}
    for section in data.get("dependencies", []):
        manager = section.get("manager")
        packages = section.get("packages", [])
        if manager == "pip":
            results["pip"] = _audit_pip(packages)
        elif manager == "npm":
            results["npm"] = _audit_npm(packages)
    return results


def format_audit(results: dict[str, list[dict]], fmt: str = "human") -> str:
    """Format audit results as human-readable text or JSON."""
    if fmt == "json":
        return json.dumps(results, indent=2)
    lines = []
    total = sum(len(v) for v in results.values())
    if total == 0:
        return "All packages up to date."
    for manager, issues in results.items():
        for issue in issues:
            current = issue.get("current", "?")
            latest = issue.get("latest", "newer version available")
            lines.append(f"[{manager}] {issue['name']} {current} -> {latest}")
    return "\n".join(lines)
