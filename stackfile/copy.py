"""Copy packages from one snapshot to another."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class CopyError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CopyError(f"File not found: {path}")
    with open(p) as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def copy_packages(
    src: dict,
    dst: dict,
    section: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[dict, int]:
    """Copy packages from src snapshot into dst snapshot.

    Returns the updated dst dict and the number of packages copied.
    """
    sections = [section] if section else ["pip", "npm", "brew"]
    copied = 0

    for sec in sections:
        src_pkgs = src.get(sec, [])
        dst_pkgs = dst.setdefault(sec, [])
        dst_names = {p["name"]: i for i, p in enumerate(dst_pkgs)}

        for pkg in src_pkgs:
            name = pkg["name"]
            if name in dst_names:
                if overwrite:
                    dst_pkgs[dst_names[name]] = dict(pkg)
                    copied += 1
            else:
                dst_pkgs.append(dict(pkg))
                copied += 1

    return dst, copied


def copy_and_save(
    src_path: str,
    dst_path: str,
    output_path: Optional[str] = None,
    section: Optional[str] = None,
    overwrite: bool = False,
) -> int:
    """Load src and dst, copy packages, write result. Returns count copied."""
    src = _load(src_path)
    dst = _load(dst_path)
    updated, count = copy_packages(src, dst, section=section, overwrite=overwrite)
    out = output_path or dst_path
    _save(updated, out)
    return count
