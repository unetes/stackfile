"""Tests for stackfile.sort module."""

import json
import pytest
from pathlib import Path

from stackfile.sort import sort_snapshot, SortError


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.3.0"},
            {"name": "attrs", "version": "23.1.0"},
        ],
        "npm": [
            {"name": "webpack", "version": "5.0.0"},
            {"name": "axios", "version": "1.4.0"},
        ],
        "brew": [
            {"name": "zsh", "version": "5.9"},
            {"name": "git", "version": "2.41.0"},
        ],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snapshot.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_sort_pip_by_name(tmp_path):
    path = write_snapshot(tmp_path)
    result = sort_snapshot(path, key="name")
    names = [p["name"] for p in result["pip"]]
    assert names == sorted(names)


def test_sort_npm_by_name_descending(tmp_path):
    path = write_snapshot(tmp_path)
    result = sort_snapshot(path, key="name", reverse=True)
    names = [p["name"] for p in result["npm"]]
    assert names == sorted(names, reverse=True)


def test_sort_by_version(tmp_path):
    path = write_snapshot(tmp_path)
    result = sort_snapshot(path, key="version")
    versions = [p["version"] for p in result["pip"]]
    assert versions == sorted(versions, key=str.lower)


def test_sort_writes_to_input_by_default(tmp_path):
    path = write_snapshot(tmp_path)
    sort_snapshot(path, key="name")
    with open(path) as f:
        saved = json.load(f)
    names = [p["name"] for p in saved["pip"]]
    assert names == sorted(names)


def test_sort_writes_to_output_path(tmp_path):
    path = write_snapshot(tmp_path)
    out = str(tmp_path / "sorted.json")
    sort_snapshot(path, output_path=out, key="name")
    assert Path(out).exists()
    with open(out) as f:
        saved = json.load(f)
    names = [p["name"] for p in saved["pip"]]
    assert names == sorted(names)


def test_sort_limited_to_sections(tmp_path):
    path = write_snapshot(tmp_path)
    original_npm = _base()["npm"]
    result = sort_snapshot(path, key="name", sections=["pip"])
    # npm should remain untouched
    assert result["npm"] == original_npm


def test_sort_invalid_key_raises(tmp_path):
    path = write_snapshot(tmp_path)
    with pytest.raises(SortError, match="Invalid sort key"):
        sort_snapshot(path, key="author")


def test_sort_missing_file_raises(tmp_path):
    with pytest.raises(SortError, match="not found"):
        sort_snapshot(str(tmp_path / "missing.json"))


def test_sort_empty_section(tmp_path):
    data = _base()
    data["pip"] = []
    path = write_snapshot(tmp_path, data)
    result = sort_snapshot(path, key="name")
    assert result["pip"] == []
