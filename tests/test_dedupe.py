"""Tests for stackfile.dedupe."""

import json
import pytest
from pathlib import Path
from stackfile.dedupe import dedupe_snapshot, DedupeError, _dedupe_packages


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": []},
        "npm": {"packages": []},
        "brew": {"packages": []},
    }


def write_snapshot(tmp_path, data):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_dedupe_packages_removes_duplicates():
    pkgs = [
        {"name": "requests", "version": "2.28.0"},
        {"name": "flask", "version": "2.0.0"},
        {"name": "requests", "version": "2.31.0"},
    ]
    result, removed = _dedupe_packages(pkgs)
    assert removed == 1
    names = [p["name"] for p in result]
    assert names == ["flask", "requests"]


def test_dedupe_packages_last_wins():
    pkgs = [
        {"name": "numpy", "version": "1.0"},
        {"name": "numpy", "version": "2.0"},
    ]
    result, _ = _dedupe_packages(pkgs)
    assert result[0]["version"] == "2.0"


def test_dedupe_packages_no_duplicates():
    pkgs = [{"name": "a"}, {"name": "b"}]
    result, removed = _dedupe_packages(pkgs)
    assert removed == 0
    assert len(result) == 2


def test_dedupe_snapshot_pip(tmp_path):
    snap = _base()
    snap["pip"]["packages"] = [
        {"name": "requests", "version": "2.0"},
        {"name": "requests", "version": "2.5"},
    ]
    path = write_snapshot(tmp_path, snap)
    report = dedupe_snapshot(path)
    assert report["pip"] == 1
    data = json.loads(Path(path).read_text())
    assert len(data["pip"]["packages"]) == 1


def test_dedupe_snapshot_writes_to_output(tmp_path):
    snap = _base()
    snap["npm"]["packages"] = [
        {"name": "lodash", "version": "4.0"},
        {"name": "lodash", "version": "4.17"},
    ]
    src = write_snapshot(tmp_path, snap)
    out = str(tmp_path / "out.json")
    dedupe_snapshot(src, output_path=out)
    data = json.loads(Path(out).read_text())
    assert len(data["npm"]["packages"]) == 1


def test_dedupe_snapshot_section_filter(tmp_path):
    snap = _base()
    snap["pip"]["packages"] = [
        {"name": "x"},
        {"name": "x"},
    ]
    snap["npm"]["packages"] = [
        {"name": "y"},
        {"name": "y"},
    ]
    path = write_snapshot(tmp_path, snap)
    report = dedupe_snapshot(path, sections=["pip"])
    assert report.get("pip") == 1
    assert "npm" not in report


def test_dedupe_missing_file_raises():
    with pytest.raises(DedupeError):
        dedupe_snapshot("/nonexistent/snap.json")
