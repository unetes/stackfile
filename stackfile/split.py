"""Split a snapshot into multiple snapshots, one per section."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class SplitError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise SplitError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def split_snapshot(
    snapshot: dict,
    sections: List[str] | None = None,
) -> Dict[str, dict]:
    """Return a dict mapping section name -> isolated snapshot dict."""
    available = ["pip", "npm", "brew"]
    targets = sections if sections else available

    results: Dict[str, dict] = {}
    for section in targets:
        if section not in available:
            raise SplitError(f"Unknown section: {section}")
        packages = snapshot.get(section, [])
        child: dict = {
            "version": snapshot.get("version", "1.0"),
            "created_at": snapshot.get("created_at", ""),
            "section": section,
            "pip": [],
            "npm": [],
            "brew": [],
        }
        child[section] = packages
        results[section] = child
    return results


def split_and_save(
    input_path: str,
    output_dir: str,
    sections: List[str] | None = None,
) -> Dict[str, str]:
    """Split snapshot file and write one file per section. Returns mapping of section->path."""
    snapshot = _load(input_path)
    split = split_snapshot(snapshot, sections)
    stem = Path(input_path).stem
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    written: Dict[str, str] = {}
    for section, data in split.items():
        dest = str(out / f"{stem}_{section}.json")
        _save(data, dest)
        written[section] = dest
    return written
