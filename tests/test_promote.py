"""Tests for stackfile.promote."""

import json
import pytest
from pathlib import Path

from stackfile.promote import (
    PromoteError,
    promote_package,
    promote_and_save,
)


def _base():
    return {
        "version": 1,
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.0.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_promote_moves_package(tmp_path):
    data = _base()
    moved = promote_package(data, "requests", "pip", "npm")
    assert moved == 1
    assert not any(p["name"] == "requests" for p in data["pip"])
    assert any(p["name"] == "requests" for p in data["npm"])


def test_promote_no_match_returns_zero():
    data = _base()
    moved = promote_package(data, "nonexistent", "pip", "npm")
    assert moved == 0


def test_promote_missing_source_section_raises():
    data = _base()
    with pytest.raises(PromoteError, match="Section 'ruby'"):
        promote_package(data, "requests", "ruby", "npm")


def test_promote_missing_dest_section_raises():
    data = _base()
    with pytest.raises(PromoteError, match="Section 'ruby'"):
        promote_package(data, "requests", "pip", "ruby")


def test_promote_conflict_raises_without_overwrite():
    data = _base()
    data["npm"].append({"name": "requests", "version": "0.1.0"})
    with pytest.raises(PromoteError, match="already exists"):
        promote_package(data, "requests", "pip", "npm", overwrite=False)


def test_promote_conflict_overwrite_replaces():
    data = _base()
    data["npm"].append({"name": "requests", "version": "0.1.0"})
    moved = promote_package(data, "requests", "pip", "npm", overwrite=True)
    assert moved == 1
    npm_requests = [p for p in data["npm"] if p["name"] == "requests"]
    assert len(npm_requests) == 1
    assert npm_requests[0]["version"] == "2.28.0"


def test_promote_and_save_writes_file(tmp_path):
    path = write_snapshot(tmp_path)
    moved = promote_and_save(path, "flask", "pip", "npm")
    assert moved == 1
    result = json.loads(Path(path).read_text())
    assert not any(p["name"] == "flask" for p in result["pip"])
    assert any(p["name"] == "flask" for p in result["npm"])


def test_promote_and_save_to_output_file(tmp_path):
    src = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    promote_and_save(src, "flask", "pip", "npm", output_path=out)
    result = json.loads(Path(out).read_text())
    assert any(p["name"] == "flask" for p in result["npm"])


def test_promote_and_save_missing_file_raises(tmp_path):
    with pytest.raises(PromoteError, match="not found"):
        promote_and_save(str(tmp_path / "missing.json"), "x", "pip", "npm")
