"""Doctor module — checks that required tools are installed and accessible."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


class DoctorError(Exception):
    """Raised when the doctor check encounters an unrecoverable error."""


@dataclass
class CheckResult:
    """Result of a single tool check."""

    tool: str
    found: bool
    version: Optional[str] = None
    hint: Optional[str] = None

    @property
    def status_label(self) -> str:
        return "ok" if self.found else "missing"


@dataclass
class DoctorReport:
    """Aggregated results from all checks."""

    results: List[CheckResult] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(r.found for r in self.results)

    def to_dict(self) -> dict:
        return {
            "all_ok": self.all_ok,
            "checks": [
                {
                    "tool": r.tool,
                    "found": r.found,
                    "version": r.version,
                    "hint": r.hint,
                }
                for r in self.results
            ],
        }


# Map of tool name -> hint shown when the tool is absent
_HINTS: dict[str, str] = {
    "pip": "Install Python (https://www.python.org/downloads/) — pip is bundled with it.",
    "npm": "Install Node.js (https://nodejs.org/) — npm is bundled with it.",
    "brew": "Install Homebrew (https://brew.sh/) — macOS/Linux package manager.",
}

_TOOLS = list(_HINTS.keys())


def _get_version(tool: str) -> Optional[str]:
    """Return the version string reported by *tool* --version, or None on failure."""
    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Use stdout if populated, otherwise fall back to stderr (npm uses stderr)
        output = (result.stdout or result.stderr or "").strip()
        # Grab just the first line to keep things tidy
        return output.splitlines()[0] if output else None
    except Exception:
        return None


def run_doctor(tools: Optional[List[str]] = None) -> DoctorReport:
    """Check whether each requested tool is installed.

    Parameters
    ----------
    tools:
        List of tool names to check.  Defaults to ``["pip", "npm", "brew"]``.

    Returns
    -------
    DoctorReport
        A report containing one :class:`CheckResult` per tool.
    """
    if tools is None:
        tools = _TOOLS

    report = DoctorReport()
    for tool in tools:
        path = shutil.which(tool)
        found = path is not None
        version = _get_version(tool) if found else None
        hint = None if found else _HINTS.get(tool, f"Install '{tool}' and ensure it is on your PATH.")
        report.results.append(CheckResult(tool=tool, found=found, version=version, hint=hint))

    return report


def format_doctor(report: DoctorReport) -> str:
    """Return a human-readable summary of *report*."""
    lines: List[str] = ["stackfile doctor\n" + "-" * 40]
    for r in report.results:
        icon = "✔" if r.found else "✘"
        version_str = f"  ({r.version})" if r.version else ""
        lines.append(f"  {icon}  {r.tool}{version_str}")
        if r.hint:
            lines.append(f"       hint: {r.hint}")
    lines.append("-" * 40)
    if report.all_ok:
        lines.append("All tools are available. You're good to go!")
    else:
        missing = [r.tool for r in report.results if not r.found]
        lines.append(f"Missing tools: {', '.join(missing)}")
    return "\n".join(lines)
