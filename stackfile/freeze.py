"""Freeze a snapshot: lock all package versions to their currently installed values."""

import json
import subprocess
from pathlib import Path
from typing import Optional


class FreezeError(Exception):
    pass


def _load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise FreezeError(f"Failed to load snapshot: {e}") from e


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _installed_pip() -> dict:
    """Return {name: version} for all installed pip packages."""
    try:
        out = subprocess.check_output(
            ["pip", "list", "--format=json"], text=True, stderr=subprocess.DEVNULL
        )
        return {pkg["name"].lower(): pkg["version"] for pkg in json.loads(out)}
    except Exception:
        return {}


def _installed_npm() -> dict:
    """Return {name: version} for globally installed npm packages."""
    try:
        out = subprocess.check_output(
            ["npm", "list", "-g", "--depth=0", "--json"], text=True, stderr=subprocess.DEVNULL
        )
        deps = json.loads(out).get("dependencies", {})
        return {name: meta.get("version", "") for name, meta in deps.items()}
    except Exception:
        return {}


def _freeze_packages(packages: list, installed: dict) -> list:
    """Replace unversioned or wildcard entries with installed versions."""
    frozen = []
    for pkg in packages:
        name = pkg.get("name", "")
        version = pkg.get("version", "")
        if not version or version in ("*", "latest"):
            resolved = installed.get(name.lower(), "")
            frozen.append({**pkg, "version": resolved if resolved else version})
        else:
            frozen.append(pkg)
    return frozen


def freeze_snapshot(input_path: str, output_path: Optional[str] = None) -> dict:
    """Freeze all package versions in a snapshot to currently installed versions."""
    data = _load(input_path)
    pip_installed = _installed_pip()
    npm_installed = _installed_npm()

    if "pip" in data:
        data["pip"] = _freeze_packages(data["pip"], pip_installed)
    if "npm" in data:
        data["npm"] = _freeze_packages(data["npm"], npm_installed)
    # brew packages typically don't carry version constraints — leave as-is

    data["frozen"] = True
    dest = output_path or input_path
    _save(data, dest)
    return data
