"""Tests for stackfile.compare."""

import json
from pathlib import Path

import pytest

from stackfile.compare import (
    CompareError,
    compare_snapshots,
    format_compare,
)


def _write(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def _snap(pip=None, npm=None, brew=None) -> dict:
    def section(pkgs):
        return {"packages": [{"name": n, "version": v} for n, v in (pkgs or {}).items()]}

    return {
        "version": "1",
        "pip": section(pip),
        "npm": section(npm),
        "brew": section(brew),
    }


def test_compare_identical_snapshots(tmp_path):
    snap = _snap(pip={"requests": "2.31.0"}, npm={"lodash": "4.17.21"})
    a = _write(tmp_path, "a.json", snap)
    b = _write(tmp_path, "b.json", snap)
    report = compare_snapshots(a, b)
    assert report["overall_similarity_pct"] == 100.0
    assert report["sections"]["pip"]["identical"] == ["requests"]


def test_compare_detects_only_in_a(tmp_path):
    a = _write(tmp_path, "a.json", _snap(pip={"flask": "3.0.0", "requests": "2.31.0"}))
    b = _write(tmp_path, "b.json", _snap(pip={"requests": "2.31.0"}))
    report = compare_snapshots(a, b)
    assert "flask" in report["sections"]["pip"]["only_in_a"]


def test_compare_detects_only_in_b(tmp_path):
    a = _write(tmp_path, "a.json", _snap(pip={"requests": "2.31.0"}))
    b = _write(tmp_path, "b.json", _snap(pip={"requests": "2.31.0", "flask": "3.0.0"}))
    report = compare_snapshots(a, b)
    assert "flask" in report["sections"]["pip"]["only_in_b"]


def test_compare_detects_version_diff(tmp_path):
    a = _write(tmp_path, "a.json", _snap(pip={"requests": "2.28.0"}))
    b = _write(tmp_path, "b.json", _snap(pip={"requests": "2.31.0"}))
    report = compare_snapshots(a, b)
    assert "requests" in report["sections"]["pip"]["version_diff"]
    assert report["sections"]["pip"]["similarity_pct"] == 0.0


def test_compare_empty_sections_are_100_pct(tmp_path):
    a = _write(tmp_path, "a.json", _snap())
    b = _write(tmp_path, "b.json", _snap())
    report = compare_snapshots(a, b)
    assert report["overall_similarity_pct"] == 100.0


def test_compare_raises_on_missing_file(tmp_path):
    a = _write(tmp_path, "a.json", _snap())
    with pytest.raises(CompareError):
        compare_snapshots(a, str(tmp_path / "missing.json"))


def test_format_compare_contains_section_headers(tmp_path):
    a = _write(tmp_path, "a.json", _snap(pip={"requests": "2.31.0"}))
    b = _write(tmp_path, "b.json", _snap(pip={"requests": "2.28.0"}))
    report = compare_snapshots(a, b)
    output = format_compare(report)
    assert "[pip]" in output
    assert "Ver diff" in output


def test_format_compare_shows_overall_similarity(tmp_path):
    snap = _snap(pip={"requests": "2.31.0"})
    a = _write(tmp_path, "a.json", snap)
    b = _write(tmp_path, "b.json", snap)
    report = compare_snapshots(a, b)
    output = format_compare(report)
    assert "100.0%" in output
