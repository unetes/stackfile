"""Tests for stackfile.mark module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.mark import MarkError, mark_package, unmark_package, mark_and_save


def _base() -> dict:
    return {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.3.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_mark_sets_status_on_matching_package():
    data = _base()
    count = mark_package(data, "requests", "deprecated")
    assert count == 1
    pkg = next(p for p in data["pip"] if p["name"] == "requests")
    assert pkg["status"] == "deprecated"


def test_mark_is_case_insensitive():
    data = _base()
    count = mark_package(data, "FLASK", "review")
    assert count == 1
    pkg = next(p for p in data["pip"] if p["name"] == "flask")
    assert pkg["status"] == "review"


def test_mark_no_match_returns_zero():
    data = _base()
    count = mark_package(data, "nonexistent", "ok")
    assert count == 0


def test_mark_section_flag_limits_scope():
    data = _base()
    # lodash is in npm, not pip — should not match when section="pip"
    count = mark_package(data, "lodash", "stable", section="pip")
    assert count == 0
    pkg = data["npm"][0]
    assert "status" not in pkg


def test_mark_section_flag_matches_correct_section():
    data = _base()
    count = mark_package(data, "lodash", "stable", section="npm")
    assert count == 1
    assert data["npm"][0]["status"] == "stable"


def test_unmark_removes_status_field():
    data = _base()
    data["pip"][0]["status"] = "deprecated"
    count = unmark_package(data, "requests")
    assert count == 1
    assert "status" not in data["pip"][0]


def test_unmark_no_status_returns_zero():
    data = _base()
    count = unmark_package(data, "requests")
    assert count == 0


def test_mark_and_save_writes_file(tmp_path):
    data = _base()
    path = write_snapshot(tmp_path, data)
    count = mark_and_save(path, "flask", "pinned")
    assert count == 1
    result = json.loads(Path(path).read_text())
    pkg = next(p for p in result["pip"] if p["name"] == "flask")
    assert pkg["status"] == "pinned"


def test_mark_and_save_to_output_file(tmp_path):
    data = _base()
    src = write_snapshot(tmp_path, data)
    out = str(tmp_path / "out.json")
    mark_and_save(src, "requests", "ok", output_path=out)
    result = json.loads(Path(out).read_text())
    pkg = next(p for p in result["pip"] if p["name"] == "requests")
    assert pkg["status"] == "ok"


def test_mark_and_save_raises_on_missing_file(tmp_path):
    with pytest.raises(MarkError):
        mark_and_save(str(tmp_path / "missing.json"), "requests", "ok")
