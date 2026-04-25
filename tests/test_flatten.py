"""Tests for stackfile.flatten."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.flatten import (
    FlattenError,
    flatten_snapshot,
    format_flat,
    flatten_and_print,
)


def _base() -> dict:
    return {
        "version": "1.0",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [
            {"name": "git", "version": "2.44.0"},
        ],
    }


def write_snapshot(tmp_path: Path, data: dict | None = None) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return p


def test_flatten_returns_all_packages():
    data = _base()
    result = flatten_snapshot(data)
    assert len(result) == 4


def test_flatten_includes_section_by_default():
    data = _base()
    result = flatten_snapshot(data)
    sections = {pkg["section"] for pkg in result}
    assert sections == {"pip", "npm", "brew"}


def test_flatten_exclude_section_field():
    data = _base()
    result = flatten_snapshot(data, include_section=False)
    for pkg in result:
        assert "section" not in pkg


def test_flatten_section_flag_limits_scope():
    data = _base()
    result = flatten_snapshot(data, section="pip")
    assert all(pkg["section"] == "pip" for pkg in result)
    assert len(result) == 2


def test_flatten_unknown_section_raises():
    with pytest.raises(FlattenError, match="Unknown section"):
        flatten_snapshot(_base(), section="cargo")


def test_flatten_empty_sections():
    data = {"pip": [], "npm": [], "brew": []}
    result = flatten_snapshot(data)
    assert result == []


def test_format_flat_human():
    packages = [
        {"name": "requests", "version": "2.31.0", "section": "pip"},
        {"name": "lodash", "version": "4.17.21", "section": "npm"},
    ]
    output = format_flat(packages)
    assert "[pip] requests==2.31.0" in output
    assert "[npm] lodash==4.17.21" in output


def test_format_flat_json():
    packages = [{"name": "flask", "version": "3.0.0", "section": "pip"}]
    output = format_flat(packages, as_json=True)
    parsed = json.loads(output)
    assert parsed[0]["name"] == "flask"


def test_format_flat_empty_message():
    assert format_flat([]) == "No packages found."


def test_flatten_and_print_missing_file():
    with pytest.raises(FlattenError, match="File not found"):
        flatten_and_print("/nonexistent/snap.json")


def test_flatten_and_print_returns_packages(tmp_path: Path):
    p = write_snapshot(tmp_path)
    result = flatten_and_print(str(p))
    assert len(result) == 4
