"""Validate a stackfile snapshot for schema correctness."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_KEYS = {"version", "created_at"}
KNOWN_SECTIONS = {"pip", "npm", "brew"}


class ValidationError(Exception):
    pass


def _load(path: str) -> dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc
    except FileNotFoundError:
        raise ValidationError(f"File not found: {path}")


def validate_snapshot(path: str) -> list[str]:
    """Return a list of validation warnings/errors. Empty list means valid."""
    errors: list[str] = []

    data = _load(path)

    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    for section in KNOWN_SECTIONS:
        if section not in data:
            continue
        section_data = data[section]
        if not isinstance(section_data, dict):
            errors.append(f"Section '{section}' must be an object")
            continue
        packages = section_data.get("packages")
        if packages is None:
            errors.append(f"Section '{section}' missing 'packages' key")
        elif not isinstance(packages, list):
            errors.append(f"Section '{section}.packages' must be an array")
        else:
            for i, pkg in enumerate(packages):
                if not isinstance(pkg, str):
                    errors.append(
                        f"Section '{section}.packages[{i}]' must be a string, got {type(pkg).__name__}"
                    )

    unknown = set(data.keys()) - REQUIRED_TOP_KEYS - KNOWN_SECTIONS
    for key in sorted(unknown):
        errors.append(f"Unknown key: '{key}'")

    return errors


def validate_or_exit(path: str) -> None:
    """Print errors and raise SystemExit(1) if snapshot is invalid."""
    errors = validate_snapshot(path)
    if errors:
        for err in errors:
            print(f"  [error] {err}")
        raise SystemExit(1)
    print(f"Snapshot '{path}' is valid.")
