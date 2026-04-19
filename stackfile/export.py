"""Export snapshot to various formats (shell script, requirements.txt, etc.)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def export_shell(snapshot: dict[str, Any]) -> str:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]

    pip_pkgs = snapshot.get("pip", {})
    if pip_pkgs:
        lines.append("# pip")
        for pkg, ver in pip_pkgs.items():
            lines.append(f"pip install '{pkg}=={ver}'")
        lines.append("")

    npm_pkgs = snapshot.get("npm", {})
    if npm_pkgs:
        lines.append("# npm (global)")
        for pkg, ver in npm_pkgs.items():
            lines.append(f"npm install -g '{pkg}@{ver}'")
        lines.append("")

    brew_pkgs = snapshot.get("brew", {})
    if brew_pkgs:
        lines.append("# brew")
        for pkg, ver in brew_pkgs.items():
            lines.append(f"brew install '{pkg}'  # {ver}")
        lines.append("")

    return "\n".join(lines)


def export_requirements_txt(snapshot: dict[str, Any]) -> str:
    pip_pkgs = snapshot.get("pip", {})
    return "\n".join(f"{pkg}=={ver}" for pkg, ver in sorted(pip_pkgs.items())) + ("\n" if pip_pkgs else "")


def export_snapshot(input_path: str, output_path: str, fmt: str) -> None:
    snapshot = _load(input_path)

    if fmt == "shell":
        content = export_shell(snapshot)
        suffix = ".sh"
    elif fmt == "requirements":
        content = export_requirements_txt(snapshot)
        suffix = ".txt"
    else:
        raise ValueError(f"Unknown export format: {fmt}")

    out = Path(output_path) if output_path else Path(input_path).with_suffix(suffix)
    out.write_text(content)
    print(f"Exported {fmt} to {out}")
