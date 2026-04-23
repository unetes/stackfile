"""Tag management for stackfile snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TagError(Exception):
    """Raised when a tagging operation fails."""


def _load(path: str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise TagError(f"Cannot load snapshot '{path}': {exc}") from exc


def _save(data: dict[str, Any], path: str) -> None:
    Path(path).write_text(json.dumps(data, indent=2))


def add_tag(snapshot_path: str, tag: str, output_path: str | None = None) -> dict[str, Any]:
    """Add a tag to a snapshot's tag list."""
    data = _load(snapshot_path)
    tags: list[str] = data.get("tags", [])
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists in snapshot.")
    tags.append(tag)
    data["tags"] = tags
    _save(data, output_path or snapshot_path)
    return data


def remove_tag(snapshot_path: str, tag: str, output_path: str | None = None) -> dict[str, Any]:
    """Remove a tag from a snapshot's tag list."""
    data = _load(snapshot_path)
    tags: list[str] = data.get("tags", [])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found in snapshot.")
    tags.remove(tag)
    data["tags"] = tags
    _save(data, output_path or snapshot_path)
    return data


def list_tags(snapshot_path: str) -> list[str]:
    """Return the list of tags for a snapshot."""
    data = _load(snapshot_path)
    return data.get("tags", [])


def rename_tag(snapshot_path: str, old_tag: str, new_tag: str, output_path: str | None = None) -> dict[str, Any]:
    """Rename an existing tag in a snapshot's tag list.

    Raises TagError if ``old_tag`` is not present or ``new_tag`` already exists.
    """
    data = _load(snapshot_path)
    tags: list[str] = data.get("tags", [])
    if old_tag not in tags:
        raise TagError(f"Tag '{old_tag}' not found in snapshot.")
    if new_tag in tags:
        raise TagError(f"Tag '{new_tag}' already exists in snapshot.")
    tags[tags.index(old_tag)] = new_tag
    data["tags"] = tags
    _save(data, output_path or snapshot_path)
    return data


def tag_and_save(action: str, snapshot_path: str, tag: str, output_path: str | None = None) -> dict[str, Any]:
    """Dispatch add/remove/list actions."""
    if action == "add":
        return add_tag(snapshot_path, tag, output_path)
    if action == "remove":
        return remove_tag(snapshot_path, tag, output_path)
    raise TagError(f"Unknown action '{action}'. Use 'add' or 'remove'.")
