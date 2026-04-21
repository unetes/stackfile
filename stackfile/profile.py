"""Profile management: save and switch named environment profiles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

DEFAULT_PROFILES_DIR = Path(".stackfile_profiles")


class ProfileError(Exception):
    pass


def _profiles_dir(base: Optional[Path] = None) -> Path:
    return base or DEFAULT_PROFILES_DIR


def list_profiles(base: Optional[Path] = None) -> list[str]:
    """Return names of all saved profiles."""
    d = _profiles_dir(base)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def save_profile(name: str, snapshot_path: Path, base: Optional[Path] = None) -> Path:
    """Copy a snapshot file into the profiles directory under *name*."""
    if not snapshot_path.exists():
        raise ProfileError(f"Snapshot not found: {snapshot_path}")
    if not name.isidentifier():
        raise ProfileError(f"Invalid profile name '{name}': use letters, digits, underscores only")
    d = _profiles_dir(base)
    d.mkdir(parents=True, exist_ok=True)
    dest = d / f"{name}.json"
    shutil.copy2(snapshot_path, dest)
    return dest


def load_profile(name: str, dest: Path, base: Optional[Path] = None) -> Path:
    """Copy a saved profile back to *dest*."""
    d = _profiles_dir(base)
    src = d / f"{name}.json"
    if not src.exists():
        raise ProfileError(f"Profile '{name}' does not exist")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def delete_profile(name: str, base: Optional[Path] = None) -> None:
    """Remove a saved profile."""
    d = _profiles_dir(base)
    src = d / f"{name}.json"
    if not src.exists():
        raise ProfileError(f"Profile '{name}' does not exist")
    src.unlink()


def show_profile(name: str, base: Optional[Path] = None) -> dict:
    """Return the parsed contents of a profile snapshot."""
    d = _profiles_dir(base)
    src = d / f"{name}.json"
    if not src.exists():
        raise ProfileError(f"Profile '{name}' does not exist")
    with src.open() as fh:
        return json.load(fh)
