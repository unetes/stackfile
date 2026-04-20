"""Tests for stackfile.search."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.search import (
    SearchError,
    format_search_results,
    search_and_print,
    search_snapshot,
)


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    data = {
        "version": "1",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [
            {"name": "express", "version": "4.18.2"},
        ],
        "brew": [
            {"name": "git", "version": "2.44.0"},
            {"name": "gh", "version": "2.47.0"},
        ],
    }
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return p


def test_search_finds_exact_match(snapshot_file: Path) -> None:
    snapshot = json.loads(snapshot_file.read_text())
    results = search_snapshot(snapshot, "requests")
    assert "pip" in results
    assert results["pip"][0]["name"] == "requests"


def test_search_finds_partial_match(snapshot_file: Path) -> None:
    snapshot = json.loads(snapshot_file.read_text())
    results = search_snapshot(snapshot, "g")  # matches git, gh
    assert "brew" in results
    assert len(results["brew"]) == 2


def test_search_case_insensitive_by_default(snapshot_file: Path) -> None:
    snapshot = json.loads(snapshot_file.read_text())
    results = search_snapshot(snapshot, "FLASK")
    assert "pip" in results
    assert results["pip"][0]["name"] == "flask"


def test_search_case_sensitive_no_match(snapshot_file: Path) -> None:
    snapshot = json.loads(snapshot_file.read_text())
    results = search_snapshot(snapshot, "FLASK", case_sensitive=True)
    assert results == {}


def test_search_no_match_returns_empty(snapshot_file: Path) -> None:
    snapshot = json.loads(snapshot_file.read_text())
    results = search_snapshot(snapshot, "nonexistent_xyz")
    assert results == {}


def test_format_results_no_matches() -> None:
    output = format_search_results({}, "missing")
    assert "No packages found" in output
    assert "missing" in output


def test_format_results_with_matches() -> None:
    results = {"pip": [{"name": "requests", "version": "2.31.0"}]}
    output = format_search_results(results, "req")
    assert "[pip]" in output
    assert "requests==2.31.0" in output


def test_search_and_print_returns_zero_on_match(snapshot_file: Path, capsys) -> None:
    code = search_and_print(str(snapshot_file), "flask")
    assert code == 0
    captured = capsys.readouterr()
    assert "flask" in captured.out


def test_search_and_print_returns_one_on_no_match(snapshot_file: Path) -> None:
    code = search_and_print(str(snapshot_file), "zzznomatch")
    assert code == 1


def test_search_and_print_missing_file(tmp_path: Path, capsys) -> None:
    code = search_and_print(str(tmp_path / "missing.json"), "flask")
    assert code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.out
