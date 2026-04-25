"""Additional tests for inspect formatting edge cases."""

import json
from stackfile.inspect import inspect_package, format_inspect


def _snap_with_extras():
    return {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {
                "name": "numpy",
                "version": "1.26.0",
                "note": "numerical computing",
                "group": "science",
                "pinned": True,
            }
        ],
        "npm": [],
        "brew": [],
    }


def test_format_human_shows_note():
    snap = _snap_with_extras()
    results = inspect_package(snap, "numpy")
    out = format_inspect(results, fmt="human")
    assert "note" in out
    assert "numerical computing" in out


def test_format_human_shows_group():
    snap = _snap_with_extras()
    results = inspect_package(snap, "numpy")
    out = format_inspect(results, fmt="human")
    assert "group" in out
    assert "science" in out


def test_format_human_shows_pinned():
    snap = _snap_with_extras()
    results = inspect_package(snap, "numpy")
    out = format_inspect(results, fmt="human")
    assert "pinned" in out


def test_format_json_includes_section_key():
    snap = _snap_with_extras()
    results = inspect_package(snap, "numpy")
    out = format_inspect(results, fmt="json")
    parsed = json.loads(out)
    assert "section" in parsed[0]
    assert parsed[0]["section"] == "pip"


def test_inspect_empty_sections_returns_empty():
    snap = {"version": "1.0", "created_at": "x", "pip": [], "npm": [], "brew": []}
    results = inspect_package(snap, "anything")
    assert results == []


def test_inspect_multiple_sections_match():
    snap = {
        "version": "1.0",
        "created_at": "x",
        "pip": [{"name": "shared", "version": "1.0"}],
        "npm": [{"name": "shared", "version": "2.0"}],
        "brew": [],
    }
    results = inspect_package(snap, "shared")
    assert len(results) == 2
    sections = {r["section"] for r in results}
    assert sections == {"pip", "npm"}


def test_format_human_multiple_results():
    snap = {
        "version": "1.0",
        "created_at": "x",
        "pip": [{"name": "shared", "version": "1.0"}],
        "npm": [{"name": "shared", "version": "2.0"}],
        "brew": [],
    }
    results = inspect_package(snap, "shared")
    out = format_inspect(results)
    assert "[pip]" in out
    assert "[npm]" in out
