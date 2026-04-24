"""Tests for stackfile.filter module."""

import json
import pytest
from pathlib import Path
from stackfile.filter import filter_snapshot, filter_and_save, FilterError


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0", "group": "http"},
            {"name": "flask", "version": "3.0.0", "group": "web"},
            {"name": "pytest", "version": "7.4.0"},
        ],
        "npm": [
            {"name": "axios", "version": "1.6.0", "group": "http"},
            {"name": "express", "version": "4.18.0"},
        ],
        "brew": [
            {"name": "git", "version": "2.42.0"},
        ],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_filter_by_name_pattern():
    result = filter_snapshot(_base(), name_pattern="flask")
    assert len(result["pip"]) == 1
    assert result["pip"][0]["name"] == "flask"


def test_filter_by_group():
    result = filter_snapshot(_base(), group="http")
    assert all(p["group"] == "http" for p in result["pip"])
    assert result["pip"][0]["name"] == "requests"
    assert len(result["npm"]) == 1
    assert result["npm"][0]["name"] == "axios"


def test_filter_by_section_only():
    result = filter_snapshot(_base(), sections=["pip"])
    # npm and brew are untouched, pip returns all
    assert len(result["pip"]) == 3
    assert len(result["npm"]) == 2


def test_filter_by_section_and_name():
    result = filter_snapshot(_base(), sections=["pip"], name_pattern="req")
    assert len(result["pip"]) == 1
    assert result["pip"][0]["name"] == "requests"
    assert len(result["npm"]) == 2  # untouched


def test_filter_by_version_pattern():
    result = filter_snapshot(_base(), version_pattern="^3")
    assert len(result["pip"]) == 1
    assert result["pip"][0]["name"] == "flask"


def test_filter_no_criteria_returns_all():
    data = _base()
    result = filter_snapshot(data)
    assert result["pip"] == data["pip"]
    assert result["npm"] == data["npm"]


def test_filter_case_insensitive_name(tmp_path):
    result = filter_snapshot(_base(), name_pattern="FLASK")
    assert len(result["pip"]) == 1


def test_filter_and_save_writes_file(tmp_path):
    src = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    result = filter_and_save(src, out, name_pattern="requests")
    assert Path(out).exists()
    saved = json.loads(Path(out).read_text())
    assert any(p["name"] == "requests" for p in saved["pip"])


def test_filter_missing_file_raises(tmp_path):
    with pytest.raises(FilterError):
        filter_and_save(str(tmp_path / "nope.json"), str(tmp_path / "out.json"))
