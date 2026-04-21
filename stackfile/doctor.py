"""Doctor: check local environment health against a snapshot."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class DoctorError(Exception):
    pass


@dataclass
class CheckResult:
    tool: str
    available: bool
    version: str | None = None
    note: str | None = None


def status_label(ok: bool) -> str:
    return "OK" if ok else "MISSING"


@dataclass
class DoctorReport:
    results: List[CheckResult] = field(default_factory=list)

    def all_ok(self) -> bool:
        return all(r.available for r in self.results)

    def to_dict(self) -> dict:
        return {
            "all_ok": self.all_ok(),
            "checks": [
                {
                    "tool": r.tool,
                    "available": r.available,
                    "version": r.version,
                    "note": r.note,
                }
                for r in self.results
            ],
        }


def _load(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise DoctorError(f"Snapshot not found: {path}")
    except json.JSONDecodeError as exc:
        raise DoctorError(f"Invalid JSON in snapshot: {exc}")


def _check_tool(tool: str) -> CheckResult:
    found = shutil.which(tool) is not None
    version = None
    if found:
        try:
            out = subprocess.check_output(
                [tool, "--version"], stderr=subprocess.STDOUT, text=True
            )
            version = out.strip().splitlines()[0]
        except Exception:
            version = "unknown"
    return CheckResult(tool=tool, available=found, version=version)


def _tools_from_snapshot(snapshot: dict) -> list[str]:
    tools = []
    section_tool_map = {"pip": "pip", "npm": "npm", "brew": "brew"}
    for section, tool in section_tool_map.items():
        packages = snapshot.get(section, [])
        if isinstance(packages, list) and packages:
            tools.append(tool)
    return tools


def run_doctor(snapshot_path: str) -> DoctorReport:
    snapshot = _load(snapshot_path)
    tools = _tools_from_snapshot(snapshot)
    if not tools:
        tools = ["pip", "npm", "brew"]
    report = DoctorReport()
    for tool in tools:
        report.results.append(_check_tool(tool))
    return report


def format_doctor(report: DoctorReport) -> str:
    lines = []
    for r in report.results:
        label = status_label(r.available)
        ver = f" ({r.version})" if r.version else ""
        note = f" — {r.note}" if r.note else ""
        lines.append(f"  [{label}] {r.tool}{ver}{note}")
    summary = "All checks passed." if report.all_ok() else "Some tools are missing."
    lines.append(f"\n{summary}")
    return "\n".join(lines)
