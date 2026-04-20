"""Pin all packages in a snapshot to their currently installed exact versions."""

import json
from datetime import datetime, timezone
from pathlib import Path


class PinError(Exception):
    pass


def _load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _pin_packages(packages: list[dict]) -> list[dict]:
    """Ensure every package entry has a pinned (non-wildcard) version."""
    pinned = []
    for pkg in packages:
        name = pkg.get("name", "")
        version = pkg.get("version", "")
        if not version or version in ("*", "latest", ""):
            raise PinError(
                f"Package '{name}' has no pinned version (got {version!r}). "
                "Run a snapshot first to capture exact versions."
            )
        pinned.append({"name": name, "version": version})
    return pinned


def pin_snapshot(input_path: str, output_path: str | None = None) -> dict:
    """Load a snapshot, validate all versions are pinned, and write the result."""
    data = _load(input_path)
    out = {
        "version": data.get("version", 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pinned": True,
    }

    for section in ("pip", "npm", "brew"):
        packages = data.get(section, [])
        out[section] = _pin_packages(packages)

    dest = output_path or input_path
    _save(out, dest)
    return out
