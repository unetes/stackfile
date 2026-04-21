"""Rename a package entry across all sections of a snapshot."""

import json
from pathlib import Path


class RenameError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise RenameError(f"Snapshot not found: {path}")
    with open(p) as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def rename_package(
    data: dict,
    old_name: str,
    new_name: str,
    section: str | None = None,
) -> tuple[dict, int]:
    """Return updated snapshot and count of renames performed."""
    renamed = 0
    sections = [section] if section else ["pip", "npm", "brew"]

    for sec in sections:
        packages = data.get(sec, [])
        if not isinstance(packages, list):
            continue
        new_packages = []
        for pkg in packages:
            if isinstance(pkg, dict):
                if pkg.get("name") == old_name:
                    pkg = dict(pkg, name=new_name)
                    renamed += 1
            elif isinstance(pkg, str):
                if pkg == old_name or pkg.startswith(old_name + "=="):
                    pkg = pkg.replace(old_name, new_name, 1)
                    renamed += 1
            new_packages.append(pkg)
        data[sec] = new_packages

    return data, renamed


def rename_and_save(
    input_path: str,
    old_name: str,
    new_name: str,
    output_path: str | None = None,
    section: str | None = None,
) -> int:
    """Rename a package and save. Returns number of renames performed."""
    if not old_name or not new_name:
        raise RenameError("old_name and new_name must not be empty")
    if old_name == new_name:
        raise RenameError("old_name and new_name are identical")

    data = _load(input_path)
    updated, count = rename_package(data, old_name, new_name, section)
    dest = output_path or input_path
    _save(updated, dest)
    return count
