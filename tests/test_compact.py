"""Tests for stackfile/compact.py"""

import json
import pytest
from pathlib import Path
from stackfile.compact import (
    compact_snapshot,
    compact_and_save,
    CompactError,
    _is_empty_package,
)


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "bare-pkg", "version": ""},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21", "group": "utils"},
            {"name": "empty-npm", "version": "", "note": ""},
        ],
        "brew": [
            {"name": "git", "version": "", "note": "version control"},
            {"name": "bare-brew", "version": ""},
        ],
    }


def write_snapshot(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return p


def test_is_empty_package_true_when_no_fields():
    assert _is_empty_package({"name": "x", "version": "", "group": "", "note": ""}) is True


def test_is_empty_package_false_when_version_set():
    assert _is_empty_package({"name": "x", "version": "1.0"}) is False


def test_is_empty_package_false_when_note_set():
    assert _is_empty_package({"name": "x", "version": "", "note": "important"}) is False


def test_is_empty_package_false_when_group_set():
    assert _is_empty_package({"name": "x", "version": "", "group": "dev"}) is False


def test_compact_removes_bare_pip_packages():
    data = _base()
    result, removed = compact_snapshot(data)
    names = [p["name"] for p in result["pip"]]
    assert "bare-pkg" not in names
    assert "requests" in names


def test_compact_removes_bare_npm_packages():
    data = _base()
    result, removed = compact_snapshot(data)
    names = [p["name"] for p in result["npm"]]
    assert "empty-npm" not in names
    assert "lodash" in names


def test_compact_keeps_package_with_note():
    data = _base()
    result, _ = compact_snapshot(data)
    names = [p["name"] for p in result["brew"]]
    assert "git" in names


def test_compact_returns_correct_removed_count():
    data = _base()
    _, removed = compact_snapshot(data)
    assert removed == 3  # bare-pkg, empty-npm, bare-brew


def test_compact_section_flag_limits_scope():
    data = _base()
    result, removed = compact_snapshot(data, section="pip")
    # npm and brew untouched
    assert len(result["npm"]) == 2
    assert len(result["brew"]) == 2
    assert removed == 1


def test_compact_invalid_section_raises():
    with pytest.raises(CompactError, match="Unknown section"):
        compact_snapshot(_base(), section="cargo")


def test_compact_preserves_metadata():
    data = _base()
    result, _ = compact_snapshot(data)
    assert result["version"] == "1"
    assert result["created_at"] == "2024-01-01"


def test_compact_and_save_writes_file(tmp_path):
    p = write_snapshot(tmp_path, _base())
    removed = compact_and_save(str(p))
    saved = json.loads(p.read_text())
    names = [pkg["name"] for pkg in saved["pip"]]
    assert "bare-pkg" not in names
    assert removed == 3


def test_compact_and_save_dry_run_does_not_modify(tmp_path):
    data = _base()
    p = write_snapshot(tmp_path, data)
    original = p.read_text()
    compact_and_save(str(p), dry_run=True)
    assert p.read_text() == original


def test_compact_missing_file_raises():
    with pytest.raises(CompactError, match="File not found"):
        compact_and_save("/nonexistent/path.json")
