"""Tests for stackfile.clone."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.clone import CloneError, clone_snapshot


def write_snapshot(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00+00:00",
        "description": "original",
        "packages": {
            "pip": [{"name": "requests", "version": "2.31.0"}],
            "npm": [{"name": "lodash", "version": "4.17.21"}],
            "brew": [{"name": "git", "version": "2.44.0"}],
        },
    }


def test_clone_creates_dest_file(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    clone_snapshot(str(src), str(dst))

    assert dst.exists()


def test_clone_copies_packages(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    result = clone_snapshot(str(src), str(dst))

    assert result["packages"]["pip"] == [{"name": "requests", "version": "2.31.0"}]


def test_clone_sets_cloned_from(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    result = clone_snapshot(str(src), str(dst))

    assert result["cloned_from"] == str(src)


def test_clone_updates_created_at(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    result = clone_snapshot(str(src), str(dst))

    assert result["created_at"] != "2024-01-01T00:00:00+00:00"


def test_clone_with_label(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    result = clone_snapshot(str(src), str(dst), label="my clone")

    assert result["description"] == "my clone"


def test_clone_filters_sections(tmp_path):
    src = tmp_path / "snap.json"
    dst = tmp_path / "clone.json"
    write_snapshot(src, _base())

    result = clone_snapshot(str(src), str(dst), sections=["pip"])

    assert result["packages"]["npm"] == []
    assert result["packages"]["brew"] == []
    assert len(result["packages"]["pip"]) == 1


def test_clone_missing_source_raises(tmp_path):
    with pytest.raises(CloneError, match="not found"):
        clone_snapshot(str(tmp_path / "missing.json"), str(tmp_path / "out.json"))
