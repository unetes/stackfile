"""Restore dev environment dependencies from a snapshot file."""

import json
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def restore_pip(packages: list[dict]) -> None:
    """Install pip packages from snapshot."""
    if not packages:
        return
    for pkg in packages:
        name = pkg["name"]
        version = pkg["version"]
        print(f"  pip: installing {name}=={version}")
        _run([sys.executable, "-m", "pip", "install", f"{name}=={version}"])


def restore_npm(packages: list[dict]) -> None:
    """Install global npm packages from snapshot."""
    if not packages:
        return
    for pkg in packages:
        name = pkg["name"]
        version = pkg["version"]
        print(f"  npm: installing {name}@{version}")
        _run(["npm", "install", "-g", f"{name}@{version}"])


def restore_brew(packages: list[dict]) -> None:
    """Install Homebrew packages from snapshot."""
    if not packages:
        return
    for pkg in packages:
        name = pkg["name"]
        print(f"  brew: installing {name}")
        _run(["brew", "install", name])


def restore_snapshot(snapshot_path: str = "stackfile.json") -> None:
    """Restore all dependencies from a snapshot file."""
    path = Path(snapshot_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {snapshot_path}")

    with path.open() as f:
        snapshot = json.load(f)

    print(f"Restoring from snapshot: {snapshot_path}")
    print(f"  Created at: {snapshot.get('created_at', 'unknown')}")

    restore_pip(snapshot.get("pip", []))
    restore_npm(snapshot.get("npm", []))
    restore_brew(snapshot.get("brew", []))

    print("Restore complete.")
