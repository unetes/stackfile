"""Tests for stackfile/trim.py."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from stackfile.trim import TrimError, trim_snapshot


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.0.0"},
            {"name": "django", "version": "4.0.0"},
        ]},
        "npm": {"packages": [
            {"name": "lodash", "version": "4.17.21"},
            {"name": "axios", "version": "1.0.0"},
        ]},
        "brew": {"packages": [
            {"name": "wget", "version": "1.21"},
        ]},
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_trim_reduces_pip_to_limit(tmp_path):
    f = write_snapshot(tmp_path)
    result = trim_snapshot(f, None, limit=2)
    data = json.loads(Path(f).read_text())
    assert len(data["pip"]["packages"]) == 2
    assert result["by_section"]["pip"] == 1


def test_trim_sorts_alphabetically(tmp_path):
    f = write_snapshot(tmp_path)
    trim_snapshot(f, None, limit=2)
    data = json.loads(Path(f).read_text())
    names = [p["name"] for p in data["pip"]["packages"]]
    assert names == sorted(names)


def test_trim_section_flag_limits_scope(tmp_path):
    f = write_snapshot(tmp_path)
    result = trim_snapshot(f, None, limit=1, section="pip")
    data = json.loads(Path(f).read_text())
    assert len(data["pip"]["packages"]) == 1
    assert len(data["npm"]["packages"]) == 2  # untouched
    assert result["by_section"].get("npm", 0) == 0


def test_trim_writes_to_output_file(tmp_path):
    f = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    trim_snapshot(f, out, limit=1)
    assert Path(out).exists()
    data = json.loads(Path(out).read_text())
    assert len(data["pip"]["packages"]) == 1


def test_trim_no_removal_when_limit_exceeds_count(tmp_path):
    f = write_snapshot(tmp_path)
    result = trim_snapshot(f, None, limit=10)
    assert result["removed"] == 0


def test_trim_raises_on_missing_file(tmp_path):
    with pytest.raises(TrimError, match="not found"):
        trim_snapshot(str(tmp_path / "missing.json"), None, limit=5)


def test_trim_raises_on_invalid_limit(tmp_path):
    f = write_snapshot(tmp_path)
    with pytest.raises(TrimError, match="positive integer"):
        trim_snapshot(f, None, limit=0)


def test_trim_total_removed_sums_all_sections(tmp_path):
    f = write_snapshot(tmp_path)
    result = trim_snapshot(f, None, limit=1)
    # pip: 3->1 (2 removed), npm: 2->1 (1 removed), brew: 1->1 (0 removed)
    assert result["removed"] == 3
