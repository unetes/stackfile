"""Tests for stackfile/inspect.py"""

import json
import pytest
from pathlib import Path
from stackfile.inspect import inspect_package, format_inspect, inspect_and_print, InspectError


def _base():
    return {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.28.0", "note": "HTTP lib"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path, data):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_inspect_finds_pip_package(tmp_path):
    snap = _base()
    results = inspect_package(snap, "requests")
    assert len(results) == 1
    assert results[0]["section"] == "pip"
    assert results[0]["version"] == "2.28.0"


def test_inspect_finds_npm_package(tmp_path):
    snap = _base()
    results = inspect_package(snap, "lodash")
    assert len(results) == 1
    assert results[0]["section"] == "npm"


def test_inspect_case_insensitive(tmp_path):
    snap = _base()
    results = inspect_package(snap, "FLASK")
    assert len(results) == 1
    assert results[0]["name"] == "flask"


def test_inspect_section_filter(tmp_path):
    snap = _base()
    results = inspect_package(snap, "requests", section="pip")
    assert len(results) == 1


def test_inspect_section_filter_miss(tmp_path):
    snap = _base()
    results = inspect_package(snap, "requests", section="npm")
    assert results == []


def test_inspect_invalid_section_raises(tmp_path):
    snap = _base()
    with pytest.raises(InspectError, match="Section"):
        inspect_package(snap, "requests", section="cargo")


def test_format_inspect_human(tmp_path):
    snap = _base()
    results = inspect_package(snap, "requests")
    out = format_inspect(results)
    assert "[pip]" in out
    assert "requests" in out
    assert "2.28.0" in out


def test_format_inspect_json(tmp_path):
    snap = _base()
    results = inspect_package(snap, "requests")
    out = format_inspect(results, fmt="json")
    parsed = json.loads(out)
    assert parsed[0]["name"] == "requests"


def test_format_inspect_not_found(tmp_path):
    out = format_inspect([])
    assert "not found" in out.lower()


def test_inspect_and_print_returns_zero(tmp_path):
    p = write_snapshot(tmp_path, _base())
    rc = inspect_and_print(p, "flask")
    assert rc == 0


def test_inspect_and_print_missing_file(tmp_path):
    rc = inspect_and_print(str(tmp_path / "missing.json"), "flask")
    assert rc == 1
