"""Tests for stackfile.reorder."""

import json
import pytest
from pathlib import Path

from stackfile.reorder import (
    ReorderError,
    reorder_package,
    reorder_and_save,
)


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "3.0.0"},
            {"name": "click", "version": "8.1.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
            {"name": "axios", "version": "1.6.0"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_reorder_moves_package_to_front():
    data = _base()
    moved = reorder_package(data, "click", 0, section="pip")
    assert moved == 1
    assert data["pip"][0]["name"] == "click"


def test_reorder_moves_package_to_end():
    data = _base()
    reorder_package(data, "requests", 99, section="pip")
    assert data["pip"][-1]["name"] == "requests"


def test_reorder_clamps_negative_index():
    data = _base()
    reorder_package(data, "flask", -5, section="pip")
    assert data["pip"][0]["name"] == "flask"


def test_reorder_no_match_returns_zero():
    data = _base()
    moved = reorder_package(data, "nonexistent", 0, section="pip")
    assert moved == 0
    assert [p["name"] for p in data["pip"]] == ["requests", "flask", "click"]


def test_reorder_all_sections_when_no_section_given():
    data = _base()
    # add same name to npm too
    data["npm"].append({"name": "requests", "version": "0.0.1"})
    moved = reorder_package(data, "requests", 0)
    assert moved == 2


def test_reorder_and_save_writes_file(tmp_path):
    data = _base()
    path = write_snapshot(tmp_path, data)
    reorder_and_save(path, "click", 0, section="pip")
    saved = json.loads(Path(path).read_text())
    assert saved["pip"][0]["name"] == "click"


def test_reorder_and_save_to_output_file(tmp_path):
    data = _base()
    src = write_snapshot(tmp_path, data)
    dest = str(tmp_path / "out.json")
    reorder_and_save(src, "flask", 0, section="pip", output_path=dest)
    saved = json.loads(Path(dest).read_text())
    assert saved["pip"][0]["name"] == "flask"
    # source unchanged
    original = json.loads(Path(src).read_text())
    assert original["pip"][0]["name"] == "requests"


def test_reorder_and_save_missing_file():
    with pytest.raises(ReorderError, match="not found"):
        reorder_and_save("/no/such/file.json", "requests", 0)
