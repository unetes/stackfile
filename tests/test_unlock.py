"""Tests for stackfile.unlock."""

import json
import pytest
from pathlib import Path

from stackfile.unlock import unlock_snapshot, UnlockError


_BASE = {
    "version": "1",
    "created_at": "2024-01-01T00:00:00",
    "pip": [
        {"name": "requests", "version": "2.31.0", "pinned": True},
        {"name": "flask", "version": "3.0.0", "pinned": False},
    ],
    "npm": [
        {"name": "lodash", "version": "4.17.21", "pinned": True},
    ],
    "brew": [
        {"name": "git", "version": "2.44.0", "pinned": True},
        {"name": "curl", "version": "*", "pinned": False},
    ],
}


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_unlock_pip_pinned_packages(tmp_path):
    path = write_snapshot(tmp_path, _BASE)
    count = unlock_snapshot(path)
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["version"] == "*"
    assert data["pip"][0]["pinned"] is False


def test_unlock_leaves_unpinned_unchanged(tmp_path):
    path = write_snapshot(tmp_path, _BASE)
    unlock_snapshot(path)
    data = json.loads(Path(path).read_text())
    flask = next(p for p in data["pip"] if p["name"] == "flask")
    assert flask["version"] == "3.0.0"
    assert flask["pinned"] is False


def test_unlock_returns_correct_count(tmp_path):
    path = write_snapshot(tmp_path, _BASE)
    count = unlock_snapshot(path)
    # requests (pip) + lodash (npm) + git (brew) = 3
    assert count == 3


def test_unlock_section_flag_limits_scope(tmp_path):
    path = write_snapshot(tmp_path, _BASE)
    count = unlock_snapshot(path, section="pip")
    data = json.loads(Path(path).read_text())
    # Only pip unlocked
    assert count == 1
    # npm still pinned
    assert data["npm"][0]["pinned"] is True


def test_unlock_writes_to_output_path(tmp_path):
    src = write_snapshot(tmp_path, _BASE)
    dest = str(tmp_path / "out.json")
    unlock_snapshot(src, output_path=dest)
    assert Path(dest).exists()
    data = json.loads(Path(dest).read_text())
    assert data["pip"][0]["pinned"] is False


def test_unlock_does_not_mutate_source_when_output_given(tmp_path):
    src = write_snapshot(tmp_path, _BASE)
    dest = str(tmp_path / "out.json")
    unlock_snapshot(src, output_path=dest)
    original = json.loads(Path(src).read_text())
    assert original["pip"][0]["pinned"] is True


def test_unlock_raises_on_missing_file(tmp_path):
    with pytest.raises(UnlockError, match="File not found"):
        unlock_snapshot(str(tmp_path / "ghost.json"))


def test_unlock_empty_sections_returns_zero(tmp_path):
    data = {"version": "1", "created_at": "2024-01-01", "pip": [], "npm": [], "brew": []}
    path = write_snapshot(tmp_path, data)
    assert unlock_snapshot(path) == 0
