"""Tests for stackfile/pivot.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.pivot import (
    PivotError,
    format_pivot,
    pivot_and_print,
    pivot_snapshot,
)


def _base() -> dict:
    return {
        "version": "1.0",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "requests", "version": "2.31.0", "group": "http"},
            {"name": "flask", "version": "3.0.0", "group": "web"},
            {"name": "pytest", "version": "8.0.0"},
        ],
        "npm": [
            {"name": "axios", "version": "1.6.0", "group": "http"},
            {"name": "express", "version": "4.18.0"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path: Path, data: dict | None = None) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return p


def test_pivot_groups_by_label(tmp_path):
    snap = write_snapshot(tmp_path)
    result = pivot_snapshot(json.loads(snap.read_text()))
    assert "http" in result
    assert any(p["name"] == "requests" for p in result["http"])
    assert any(p["name"] == "axios" for p in result["http"])


def test_pivot_ungrouped_key(tmp_path):
    snap = write_snapshot(tmp_path)
    result = pivot_snapshot(json.loads(snap.read_text()))
    assert "(ungrouped)" in result
    names = [p["name"] for p in result["(ungrouped)"]]
    assert "pytest" in names
    assert "express" in names


def test_pivot_section_flag_limits_scope(tmp_path):
    snap = write_snapshot(tmp_path)
    result = pivot_snapshot(json.loads(snap.read_text()), section="pip")
    # npm packages should not appear
    all_sections = {p["section"] for pkgs in result.values() for p in pkgs}
    assert all_sections == {"pip"}


def test_pivot_unknown_section_raises(tmp_path):
    snap = write_snapshot(tmp_path)
    with pytest.raises(PivotError, match="Unknown section"):
        pivot_snapshot(json.loads(snap.read_text()), section="cargo")


def test_pivot_missing_file_raises(tmp_path):
    with pytest.raises(PivotError, match="File not found"):
        from stackfile.pivot import _load
        _load(str(tmp_path / "missing.json"))


def test_format_pivot_human_contains_group_label(tmp_path):
    grouped = {"http": [{"name": "requests", "version": "2.31.0", "section": "pip"}]}
    output = format_pivot(grouped, fmt="human")
    assert "[http]" in output
    assert "requests" in output
    assert "(pip)" in output


def test_format_pivot_json_is_valid(tmp_path):
    grouped = {"web": [{"name": "flask", "version": "3.0.0", "section": "pip"}]}
    output = format_pivot(grouped, fmt="json")
    parsed = json.loads(output)
    assert "web" in parsed


def test_format_pivot_empty_returns_message():
    output = format_pivot({}, fmt="human")
    assert "No packages found" in output


def test_pivot_and_print_exit_zero(tmp_path, capsys):
    snap = write_snapshot(tmp_path)
    code = pivot_and_print(str(snap))
    assert code == 0
    out = capsys.readouterr().out
    assert "http" in out


def test_pivot_and_print_writes_output_file(tmp_path):
    snap = write_snapshot(tmp_path)
    out_file = tmp_path / "pivot_out.json"
    pivot_and_print(str(snap), output_path=str(out_file))
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "http" in data
