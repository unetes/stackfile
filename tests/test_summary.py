"""Tests for stackfile.summary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.summary import (
    SummaryError,
    _load,
    format_summary,
    summarize_snapshot,
    summarize_and_print,
)


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "tags": ["dev"],
        "description": "test env",
        "pip": {"packages": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "*"},
        ]},
        "npm": {"packages": [
            {"name": "lodash", "version": "4.17.21"},
        ]},
        "brew": {"packages": []},
    }


def test_load_missing_file():
    with pytest.raises(SummaryError, match="not found"):
        _load("/nonexistent/path/stack.json")


def test_summarize_counts_packages(tmp_path):
    summary = summarize_snapshot(_base())
    assert summary["sections"]["pip"]["count"] == 2
    assert summary["sections"]["npm"]["count"] == 1
    assert summary["sections"]["brew"]["count"] == 0


def test_summarize_total_packages():
    summary = summarize_snapshot(_base())
    assert summary["total_packages"] == 3


def test_summarize_pinned_vs_unpinned():
    summary = summarize_snapshot(_base())
    pip = summary["sections"]["pip"]
    assert pip["pinned"] == 1
    assert pip["unpinned"] == 1


def test_summarize_metadata():
    summary = summarize_snapshot(_base())
    assert summary["version"] == "1"
    assert summary["created_at"] == "2024-01-01T00:00:00"
    assert summary["tags"] == ["dev"]
    assert summary["description"] == "test env"


def test_format_summary_contains_section_names():
    summary = summarize_snapshot(_base())
    output = format_summary(summary)
    assert "pip" in output
    assert "npm" in output
    assert "brew" in output


def test_format_summary_shows_total():
    summary = summarize_snapshot(_base())
    output = format_summary(summary)
    assert "3" in output


def test_summarize_and_print_json(tmp_path, capsys):
    path = write_snapshot(tmp_path, _base())
    result = summarize_and_print(path, as_json=True)
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["total_packages"] == result["total_packages"]


def test_summarize_and_print_human(tmp_path, capsys):
    path = write_snapshot(tmp_path, _base())
    summarize_and_print(path, as_json=False)
    captured = capsys.readouterr()
    assert "pip" in captured.out
    assert "Total pkgs" in captured.out
