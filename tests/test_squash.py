"""Tests for stackfile.squash."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.squash import SquashError, squash_snapshots, squash_and_save


def _write(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def _base(pip=None, npm=None, brew=None) -> dict:
    return {
        "version": 1,
        "created_at": "2024-01-01T00:00:00",
        "description": "base",
        "pip": pip or [],
        "npm": npm or [],
        "brew": brew or [],
    }


def test_squash_single_snapshot(tmp_path):
    path = _write(tmp_path, "a.json", _base(pip=[{"name": "requests", "version": "2.28.0"}]))
    result = squash_snapshots([path])
    assert result["pip"] == [{"name": "requests", "version": "2.28.0"}]


def test_squash_later_wins_on_conflict(tmp_path):
    a = _write(tmp_path, "a.json", _base(pip=[{"name": "requests", "version": "2.0.0"}]))
    b = _write(tmp_path, "b.json", _base(pip=[{"name": "requests", "version": "2.99.0"}]))
    result = squash_snapshots([a, b])
    assert len(result["pip"]) == 1
    assert result["pip"][0]["version"] == "2.99.0"


def test_squash_combines_unique_packages(tmp_path):
    a = _write(tmp_path, "a.json", _base(pip=[{"name": "flask", "version": "2.0.0"}]))
    b = _write(tmp_path, "b.json", _base(pip=[{"name": "django", "version": "4.0.0"}]))
    result = squash_snapshots([a, b])
    names = {p["name"] for p in result["pip"]}
    assert names == {"flask", "django"}


def test_squash_merges_all_sections(tmp_path):
    a = _write(tmp_path, "a.json", _base(
        pip=[{"name": "requests", "version": "2.0"}],
        npm=[{"name": "lodash", "version": "4.0.0"}],
        brew=[{"name": "git", "version": "2.40"}],
    ))
    b = _write(tmp_path, "b.json", _base(
        pip=[{"name": "flask", "version": "2.0"}],
        npm=[{"name": "axios", "version": "1.0.0"}],
    ))
    result = squash_snapshots([a, b])
    assert len(result["pip"]) == 2
    assert len(result["npm"]) == 2
    assert len(result["brew"]) == 1


def test_squash_records_source_paths(tmp_path):
    a = _write(tmp_path, "a.json", _base())
    b = _write(tmp_path, "b.json", _base())
    result = squash_snapshots([a, b])
    assert result["squashed_from"] == [a, b]


def test_squash_custom_label(tmp_path):
    a = _write(tmp_path, "a.json", _base())
    result = squash_snapshots([a], label="my label")
    assert result["description"] == "my label"


def test_squash_no_paths_raises(tmp_path):
    with pytest.raises(SquashError, match="At least one"):
        squash_snapshots([])


def test_squash_missing_file_raises(tmp_path):
    with pytest.raises(SquashError, match="File not found"):
        squash_snapshots([str(tmp_path / "missing.json")])


def test_squash_and_save_writes_file(tmp_path):
    a = _write(tmp_path, "a.json", _base(pip=[{"name": "requests", "version": "2.0"}]))
    out = str(tmp_path / "squashed.json")
    result = squash_and_save([a], out)
    assert Path(out).exists()
    loaded = json.loads(Path(out).read_text())
    assert loaded["pip"] == result["pip"]
