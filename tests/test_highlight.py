"""Tests for stackfile.highlight module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.highlight import (
    HighlightError,
    highlight_packages,
    format_highlight,
    highlight_and_print,
)


def _base() -> dict:
    return {
        "version": "1.0",
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.3.0", "note": "web framework"},
        ],
        "npm": [
            {"name": "react", "version": "18.0.0"},
            {"name": "react-dom", "version": "18.0.0"},
        ],
        "brew": [
            {"name": "git", "version": "2.40.0"},
        ],
    }


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_highlight_finds_exact_match(tmp_path):
    results = highlight_packages(_base(), "requests")
    assert "pip" in results
    assert results["pip"][0]["name"] == "requests"


def test_highlight_finds_partial_match(tmp_path):
    results = highlight_packages(_base(), "react")
    assert "npm" in results
    assert len(results["npm"]) == 2


def test_highlight_case_insensitive_default(tmp_path):
    results = highlight_packages(_base(), "FLASK")
    assert "pip" in results
    assert results["pip"][0]["name"] == "flask"


def test_highlight_case_sensitive_no_match(tmp_path):
    results = highlight_packages(_base(), "FLASK", case_sensitive=True)
    assert results == {}


def test_highlight_section_flag_limits_scope(tmp_path):
    results = highlight_packages(_base(), "react", section="pip")
    assert results == {}


def test_highlight_unknown_section_raises(tmp_path):
    with pytest.raises(HighlightError, match="Unknown section"):
        highlight_packages(_base(), "x", section="cargo")


def test_format_highlight_no_results():
    output = format_highlight({}, "missing")
    assert "No packages" in output
    assert "missing" in output


def test_format_highlight_human_output():
    results = {"pip": [{"name": "flask", "version": "2.3.0", "note": "web framework"}]}
    output = format_highlight(results, "flask")
    assert "[pip]" in output
    assert "flask==2.3.0" in output
    assert "web framework" in output


def test_format_highlight_json_flag():
    results = {"pip": [{"name": "requests", "version": "2.28.0"}]}
    output = format_highlight(results, "req", as_json=True)
    parsed = json.loads(output)
    assert "pip" in parsed


def test_highlight_and_print_returns_zero_on_match(tmp_path, capsys):
    path = write_snapshot(tmp_path, _base())
    code = highlight_and_print(path, "flask")
    assert code == 0
    captured = capsys.readouterr()
    assert "flask" in captured.out


def test_highlight_and_print_returns_one_on_no_match(tmp_path):
    path = write_snapshot(tmp_path, _base())
    code = highlight_and_print(path, "nonexistent_xyz")
    assert code == 1


def test_highlight_missing_file_raises(tmp_path):
    with pytest.raises(HighlightError, match="Snapshot not found"):
        highlight_and_print(str(tmp_path / "missing.json"), "flask")
