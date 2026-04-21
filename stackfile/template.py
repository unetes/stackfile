"""Generate a blank or pre-filled snapshot template."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = "1.0"

PRESETS: dict[str, dict] = {
    "python": {
        "pip": [
            {"name": "requests", "version": "*"},
            {"name": "click", "version": "*"},
        ],
        "npm": [],
        "brew": [],
    },
    "node": {
        "pip": [],
        "npm": [
            {"name": "typescript", "version": "*"},
            {"name": "eslint", "version": "*"},
        ],
        "brew": [],
    },
    "fullstack": {
        "pip": [
            {"name": "fastapi", "version": "*"},
            {"name": "uvicorn", "version": "*"},
        ],
        "npm": [
            {"name": "react", "version": "*"},
            {"name": "vite", "version": "*"},
        ],
        "brew": [
            {"name": "postgresql", "version": "*"},
        ],
    },
}


class TemplateError(Exception):
    pass


def _blank_snapshot(description: str = "") -> dict:
    return {
        "version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "tags": [],
        "pip": [],
        "npm": [],
        "brew": [],
    }


def generate_template(preset: Optional[str] = None, description: str = "") -> dict:
    """Return a snapshot dict for the given preset (or blank if None)."""
    snapshot = _blank_snapshot(description)
    if preset is None:
        return snapshot
    preset_lower = preset.lower()
    if preset_lower not in PRESETS:
        raise TemplateError(
            f"Unknown preset '{preset}'. Available: {', '.join(PRESETS)}"
        )
    snapshot.update(PRESETS[preset_lower])
    return snapshot


def save_template(output: str, preset: Optional[str] = None, description: str = "") -> dict:
    """Generate a template snapshot and write it to *output*."""
    snapshot = generate_template(preset=preset, description=description)
    Path(output).write_text(json.dumps(snapshot, indent=2))
    return snapshot
