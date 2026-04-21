"""scaffold.py — Generate a starter stackfile by inspecting the current environment.

Detects installed tools (pip, npm, brew) and builds an initial snapshot
from whatever is actually present on the machine, rather than requiring
the user to author one from scratch.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT = "stackfile.json"


class ScaffoldError(Exception):
    """Raised when scaffolding cannot complete successfully."""


def _run(cmd: list[str]) -> str:
    """Run *cmd* and return stdout; return empty string on any failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _detect_pip() -> list[dict[str, str]]:
    """Return a list of {name, version} dicts for pip-installed packages."""
    output = _run([sys.executable, "-m", "pip", "list", "--format=json"])
    if not output:
        return []
    try:
        raw: list[dict[str, str]] = json.loads(output)
        return [{"name": p["name"], "version": p["version"]} for p in raw]
    except (json.JSONDecodeError, KeyError):
        return []


def _detect_npm() -> list[dict[str, str]]:
    """Return a list of {name, version} dicts for globally installed npm packages."""
    output = _run(["npm", "list", "-g", "--depth=0", "--json"])
    if not output:
        return []
    try:
        data = json.loads(output)
        deps: dict[str, Any] = data.get("dependencies", {})
        return [
            {"name": name, "version": info.get("version", "*")}
            for name, info in deps.items()
        ]
    except (json.JSONDecodeError, AttributeError):
        return []


def _detect_brew() -> list[dict[str, str]]:
    """Return a list of {name, version} dicts for Homebrew-installed formulae."""
    output = _run(["brew", "list", "--versions"])
    if not output:
        return []
    packages: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            packages.append({"name": parts[0], "version": parts[-1]})
        elif len(parts) == 1:
            packages.append({"name": parts[0], "version": "*"})
    return packages


def scaffold_snapshot(
    *,
    include_pip: bool = True,
    include_npm: bool = True,
    include_brew: bool = True,
    description: str = "Scaffolded from current environment",
) -> dict[str, Any]:
    """Inspect the running environment and return a snapshot dict.

    Parameters
    ----------
    include_pip:  Detect pip packages when *True* (default).
    include_npm:  Detect npm global packages when *True* (default).
    include_brew: Detect Homebrew formulae when *True* (default).
    description:  Human-readable description stored in the snapshot.
    """
    snapshot: dict[str, Any] = {
        "version": "1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "pip": {"packages": _detect_pip() if include_pip else []},
        "npm": {"packages": _detect_npm() if include_npm else []},
        "brew": {"packages": _detect_brew() if include_brew else []},
    }
    return snapshot


def save_scaffold(
    snapshot: dict[str, Any],
    output_path: str = DEFAULT_OUTPUT,
    *,
    overwrite: bool = False,
) -> Path:
    """Write *snapshot* to *output_path* as JSON.

    Raises
    ------
    ScaffoldError
        If the file already exists and *overwrite* is *False*.
    """
    path = Path(output_path)
    if path.exists() and not overwrite:
        raise ScaffoldError(
            f"{path} already exists. Pass overwrite=True or choose a different path."
        )
    path.write_text(json.dumps(snapshot, indent=2))
    return path


def scaffold_and_save(
    output_path: str = DEFAULT_OUTPUT,
    *,
    include_pip: bool = True,
    include_npm: bool = True,
    include_brew: bool = True,
    description: str = "Scaffolded from current environment",
    overwrite: bool = False,
) -> Path:
    """Convenience wrapper: scaffold then save, returning the written *Path*."""
    snapshot = scaffold_snapshot(
        include_pip=include_pip,
        include_npm=include_npm,
        include_brew=include_brew,
        description=description,
    )
    return save_scaffold(snapshot, output_path, overwrite=overwrite)
