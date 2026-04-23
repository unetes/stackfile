"""Clone a snapshot, optionally filtering to specific sections."""

from __future__ import annotations

import json
import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class CloneError(Exception):
    pass


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CloneError(f"Snapshot not found: {path}")
    with p.open() as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def clone_snapshot(
    source: str,
    dest: str,
    sections: Optional[List[str]] = None,
    label: Optional[str] = None,
) -> dict:
    """Clone *source* snapshot into *dest*.

    Args:
        source: Path to the source snapshot JSON.
        dest:   Path to write the cloned snapshot JSON.
        sections: If provided, only these top-level package sections are copied
                  (e.g. ["pip", "npm"]).  All other sections are set to [].
        label:  Optional description override for the clone.

    Returns:
        The cloned snapshot dict.
    """
    data = _load(source)

    cloned = copy.deepcopy(data)
    cloned["created_at"] = datetime.now(timezone.utc).isoformat()
    cloned["cloned_from"] = str(source)

    if label is not None:
        cloned["description"] = label

    if sections is not None:
        all_sections = {"pip", "npm", "brew"}
        for sec in all_sections:
            if sec not in sections:
                cloned.setdefault("packages", {})
                if isinstance(cloned.get("packages"), dict):
                    cloned["packages"][sec] = []
                else:
                    cloned[sec] = []

    _save(cloned, dest)
    return cloned
