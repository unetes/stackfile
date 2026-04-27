"""Tests for stackfile.classify."""
import json
import pytest
from pathlib import Path
from stackfile.classify import (
    ClassifyError,
    _classify_package,
    classify_snapshot,
    format_classify,
    classify_and_print,
)


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "pytest", "version": "7.4.0"},
        ],
        "npm": [
            {"name": "express", "version": "4.18.0"},
            {"name": "eslint", "version": "8.0.0"},
        ],
        "brew": [
            {"name": "git", "version": "2.43.0"},
            {"name": "ffmpeg", "version": "6.1"},
        ],
    }


def write_snapshot(tmp_path, data):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_classify_package_pip_dev():
    assert _classify_package("pytest", "pip") == "dev"


def test_classify_package_pip_runtime():
    assert _classify_package("requests", "pip") == "runtime"


def test_classify_package_npm_dev():
    assert _classify_package("eslint", "npm") == "dev"


def test_classify_package_npm_runtime():
    assert _classify_package("express", "npm") == "runtime"


def test_classify_package_brew_system():
    assert _classify_package("git", "brew") == "system"


def test_classify_package_brew_tool():
    assert _classify_package("ffmpeg", "brew") == "tool"


def test_classify_snapshot_all_sections():
    snap = _base()
    results = classify_snapshot(snap)
    assert "pip" in results
    assert "npm" in results
    assert "brew" in results


def test_classify_snapshot_pip_categories():
    snap = _base()
    results = classify_snapshot(snap)
    cats = {p["name"]: p["category"] for p in results["pip"]}
    assert cats["requests"] == "runtime"
    assert cats["pytest"] == "dev"


def test_classify_snapshot_section_flag_limits_scope():
    snap = _base()
    results = classify_snapshot(snap, section="pip")
    assert "pip" in results
    assert "npm" not in results


def test_classify_snapshot_missing_section_skipped():
    snap = {"version": "1", "pip": [{"name": "flask", "version": "3.0"}]}
    results = classify_snapshot(snap)
    assert "pip" in results
    assert results.get("npm", []) == []


def test_format_classify_human(capsys):
    snap = _base()
    results = classify_snapshot(snap, section="pip")
    output = format_classify(results, fmt="human")
    assert "requests" in output
    assert "runtime" in output


def test_format_classify_json():
    snap = _base()
    results = classify_snapshot(snap, section="pip")
    output = format_classify(results, fmt="json")
    data = json.loads(output)
    assert "pip" in data


def test_classify_and_print_runs(tmp_path, capsys):
    path = write_snapshot(tmp_path, _base())
    classify_and_print(path, fmt="human")
    captured = capsys.readouterr()
    assert "pip" in captured.out


def test_classify_missing_file_raises():
    with pytest.raises(ClassifyError):
        from stackfile.classify import _load
        _load("/nonexistent/path.json")
