"""alias.py – Manage short aliases for snapshot file paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

ALIAS_FILE = Path.home() / ".stackfile" / "aliases.json"


class AliasError(Exception):
    pass


def _load(alias_file: Path = ALIAS_FILE) -> Dict[str, str]:
    if not alias_file.exists():
        return {}
    with alias_file.open() as fh:
        return json.load(fh)


def _save(aliases: Dict[str, str], alias_file: Path = ALIAS_FILE) -> None:
    alias_file.parent.mkdir(parents=True, exist_ok=True)
    with alias_file.open("w") as fh:
        json.dump(aliases, fh, indent=2)


def add_alias(name: str, path: str, alias_file: Path = ALIAS_FILE) -> None:
    """Register *name* as an alias for *path*."""
    if not name.isidentifier():
        raise AliasError(f"Invalid alias name: {name!r}. Must be a valid identifier.")
    aliases = _load(alias_file)
    aliases[name] = str(path)
    _save(aliases, alias_file)


def remove_alias(name: str, alias_file: Path = ALIAS_FILE) -> bool:
    """Remove alias *name*. Returns True if it existed, False otherwise."""
    aliases = _load(alias_file)
    if name not in aliases:
        return False
    del aliases[name]
    _save(aliases, alias_file)
    return True


def resolve_alias(name: str, alias_file: Path = ALIAS_FILE) -> Optional[str]:
    """Return the path registered for *name*, or None if not found."""
    return _load(alias_file).get(name)


def list_aliases(alias_file: Path = ALIAS_FILE) -> Dict[str, str]:
    """Return all registered aliases."""
    return _load(alias_file)


def resolve_path_or_alias(value: str, alias_file: Path = ALIAS_FILE) -> str:
    """If *value* is a known alias return its path, otherwise return *value* unchanged."""
    resolved = resolve_alias(value, alias_file)
    return resolved if resolved is not None else value
