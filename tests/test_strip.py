"""Tests for stackfile.strip."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.strip import (
    DEFAULT_STRIP_FIELDS,
    StripError,
    strip_and_save,
    strip_snapshot,
)


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "description": "dev env",
        "pinned": True,
        "tags": ["work"],
        "cloned_from": "old.json",
        "pip": [{"name": "requests", "version": "2.31.0", "note": "http lib"}],
        "npm": [],
        "brew": [],
    }


def write_snapshot(tmp_path: Path, data: dict | None = None) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return p


# --- strip_snapshot unit tests ---

def test_strip_removes_default_fields():
    data = _base()
    cleaned, removed = strip_snapshot(data)
    for field in DEFAULT_STRIP_FIELDS:
        assert field not in cleaned
    assert set(removed) == set(DEFAULT_STRIP_FIELDS)


def test_strip_keeps_version_and_packages():
    data = _base()
    cleaned, _ = strip_snapshot(data)
    assert cleaned["version"] == "1"
    assert cleaned["pip"] == data["pip"]


def test_strip_custom_fields():
    data = _base()
    cleaned, removed = strip_snapshot(data, fields=["tags"])
    assert "tags" not in cleaned
    assert "description" in cleaned  # not stripped
    assert removed == ["tags"]


def test_strip_missing_field_not_in_removed():
    data = {"version": "1", "pip": []}
    _, removed = strip_snapshot(data, fields=["tags", "pinned"])
    assert removed == []


def test_strip_notes_removes_note_from_packages():
    data = _base()
    cleaned, _ = strip_snapshot(data, fields=[], strip_notes=True)
    for pkg in cleaned["pip"]:
        assert "note" not in pkg


def test_strip_notes_false_keeps_notes():
    data = _base()
    cleaned, _ = strip_snapshot(data, fields=[], strip_notes=False)
    assert cleaned["pip"][0]["note"] == "http lib"


def test_strip_does_not_mutate_input():
    data = _base()
    original_keys = set(data.keys())
    strip_snapshot(data)
    assert set(data.keys()) == original_keys


# --- strip_and_save integration tests ---

def test_strip_and_save_overwrites_input(tmp_path):
    p = write_snapshot(tmp_path)
    strip_and_save(str(p))
    result = json.loads(p.read_text())
    assert "created_at" not in result
    assert "version" in result


def test_strip_and_save_to_output_file(tmp_path):
    p = write_snapshot(tmp_path)
    out = tmp_path / "clean.json"
    strip_and_save(str(p), output_path=str(out))
    assert out.exists()
    result = json.loads(out.read_text())
    assert "tags" not in result


def test_strip_and_save_missing_file_raises(tmp_path):
    with pytest.raises(StripError, match="not found"):
        strip_and_save(str(tmp_path / "missing.json"))


def test_strip_and_save_returns_removed_fields(tmp_path):
    p = write_snapshot(tmp_path)
    removed = strip_and_save(str(p))
    assert "created_at" in removed
    assert "tags" in removed
