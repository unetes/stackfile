"""Tests for stackfile/score.py"""
import json
import pytest
from pathlib import Path
from stackfile.score import (
    ScoreError,
    score_snapshot,
    format_score,
    _grade,
    _section_score,
)


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base(**kwargs):
    return {"version": "1", "created_at": "2024-01-01", "pip": [], "npm": [], "brew": [], **kwargs}


# --- _grade ---

def test_grade_a():
    assert _grade(95) == "A"

def test_grade_b():
    assert _grade(80) == "B"

def test_grade_c():
    assert _grade(65) == "C"

def test_grade_d():
    assert _grade(45) == "D"

def test_grade_f():
    assert _grade(30) == "F"


# --- _section_score ---

def test_section_score_empty_returns_100():
    m = _section_score([])
    assert m["score"] == 100
    assert m["total"] == 0

def test_section_score_all_versioned_pinned_annotated():
    pkgs = [{"name": "x", "version": "1.0.0", "pinned": True, "note": "hi"}]
    m = _section_score(pkgs)
    assert m["score"] == 100

def test_section_score_no_version_no_pin():
    pkgs = [{"name": "x", "version": "*"}]
    m = _section_score(pkgs)
    assert m["score"] == 0

def test_section_score_partial():
    pkgs = [
        {"name": "a", "version": "1.0", "pinned": True},
        {"name": "b", "version": "latest"},
    ]
    m = _section_score(pkgs)
    assert 0 < m["score"] < 100


# --- score_snapshot ---

def test_score_empty_snapshot_returns_100(tmp_path):
    path = write_snapshot(tmp_path, _base())
    report = score_snapshot(path)
    assert report["overall"] == 100
    assert report["grade"] == "A"

def test_score_missing_file_raises(tmp_path):
    with pytest.raises(ScoreError):
        score_snapshot(str(tmp_path / "nope.json"))

def test_score_counts_total_packages(tmp_path):
    data = _base(
        pip=[{"name": "requests", "version": "2.31.0"}],
        npm=[{"name": "lodash", "version": "4.17.21"}],
    )
    path = write_snapshot(tmp_path, data)
    report = score_snapshot(path)
    assert report["total_packages"] == 2

def test_score_sections_present(tmp_path):
    path = write_snapshot(tmp_path, _base())
    report = score_snapshot(path)
    assert "pip" in report["sections"]
    assert "npm" in report["sections"]
    assert "brew" in report["sections"]

def test_score_unpinned_lowers_score(tmp_path):
    data = _base(pip=[{"name": "flask", "version": "*"}])
    path = write_snapshot(tmp_path, data)
    report = score_snapshot(path)
    assert report["overall"] < 100


# --- format_score ---

def test_format_score_contains_overall(tmp_path):
    path = write_snapshot(tmp_path, _base())
    report = score_snapshot(path)
    out = format_score(report)
    assert "Overall score" in out

def test_format_score_contains_sections(tmp_path):
    path = write_snapshot(tmp_path, _base())
    report = score_snapshot(path)
    out = format_score(report)
    assert "[pip]" in out
    assert "[npm]" in out
    assert "[brew]" in out
