"""Tests for stackfile.mask."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.mask import MaskError, mask_snapshot, mask_and_save, _mask_value


def _base() -> dict:
    return {
        "version": "1.0",
        "created_at": "2024-01-01",
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


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_mask_value_full():
    assert _mask_value("2.31.0") == "******"


def test_mask_value_keep_last_two():
    result = _mask_value("2.31.0", keep=2)
    assert result.endswith(".0")
    assert result.startswith("*")


def test_mask_value_empty_string():
    assert _mask_value("") == ""


def test_mask_all_versions_no_pattern():
    data = _base()
    result, count = mask_snapshot(data)
    assert count == 4
    for pkg in result["pip"] + result["npm"] + result["brew"]:
        assert set(pkg["version"]) == {"*"}


def test_mask_by_pattern():
    data = _base()
    result, count = mask_snapshot(data, pattern="requests")
    assert count == 1
    assert result["pip"][0]["version"] == "*" * len("2.31.0")
    assert result["pip"][1]["version"] == "3.0.0"  # unchanged


def test_mask_section_limits_scope():
    data = _base()
    result, count = mask_snapshot(data, section="pip")
    assert count == 2
    # npm and brew untouched
    assert result["npm"][0]["version"] == "4.17.21"
    assert result["brew"][0]["version"] == "2.44.0"


def test_mask_custom_char():
    data = _base()
    result, count = mask_snapshot(data, pattern="flask", char="X")
    assert result["pip"][1]["version"] == "XXXXX"


def test_mask_field_name():
    data = _base()
    for pkg in data["pip"]:
        pkg["token"] = "secret123"
    result, count = mask_snapshot(data, field="token", section="pip")
    assert count == 2
    for pkg in result["pip"]:
        assert set(pkg["token"]) == {"*"}


def test_mask_does_not_mutate_input():
    data = _base()
    original_version = data["pip"][0]["version"]
    mask_snapshot(data)
    assert data["pip"][0]["version"] == original_version


def test_mask_invalid_section_raises():
    with pytest.raises(MaskError, match="Unknown section"):
        mask_snapshot(_base(), section="cargo")


def test_mask_and_save_writes_file(tmp_path):
    data = _base()
    src = write_snapshot(tmp_path, data)
    out = str(tmp_path / "out.json")
    count = mask_and_save(src, out, pattern="requests")
    assert count == 1
    saved = json.loads(Path(out).read_text())
    assert saved["pip"][0]["version"] == "*" * len("2.31.0")


def test_mask_and_save_missing_file_raises(tmp_path):
    with pytest.raises(MaskError, match="File not found"):
        mask_and_save(str(tmp_path / "nope.json"), str(tmp_path / "out.json"))
