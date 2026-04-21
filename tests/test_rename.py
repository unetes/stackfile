"""Tests for stackfile.rename."""

import json
import pytest
from pathlib import Path
from stackfile.rename import rename_package, rename_and_save, RenameError


def write_snapshot(tmp_path, data):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [{"name": "git", "version": "2.40.0"}],
    }


def test_rename_pip_package():
    data, count = rename_package(_base(), "requests", "httpx", section="pip")
    names = [p["name"] for p in data["pip"]]
    assert "httpx" in names
    assert "requests" not in names
    assert count == 1


def test_rename_across_all_sections():
    snap = _base()
    snap["npm"].append({"name": "requests", "version": "1.0.0"})
    data, count = rename_package(snap, "requests", "httpx")
    assert count == 2
    pip_names = [p["name"] for p in data["pip"]]
    npm_names = [p["name"] for p in data["npm"]]
    assert "httpx" in pip_names
    assert "httpx" in npm_names


def test_rename_no_match_returns_zero():
    data, count = rename_package(_base(), "nonexistent", "other")
    assert count == 0


def test_rename_string_package():
    snap = {"pip": ["requests==2.28.0"], "npm": [], "brew": []}
    data, count = rename_package(snap, "requests", "httpx", section="pip")
    assert data["pip"] == ["httpx==2.28.0"]
    assert count == 1


def test_rename_and_save_writes_file(tmp_path):
    p = write_snapshot(tmp_path, _base())
    count = rename_and_save(p, "requests", "httpx", section="pip")
    result = json.loads(Path(p).read_text())
    assert result["pip"][0]["name"] == "httpx"
    assert count == 1


def test_rename_and_save_to_output_path(tmp_path):
    src = write_snapshot(tmp_path, _base())
    out = str(tmp_path / "out.json")
    rename_and_save(src, "requests", "httpx", output_path=out)
    result = json.loads(Path(out).read_text())
    assert result["pip"][0]["name"] == "httpx"


def test_rename_raises_on_same_name():
    with pytest.raises(RenameError, match="identical"):
        rename_and_save("/dev/null", "foo", "foo")


def test_rename_raises_on_empty_name(tmp_path):
    p = write_snapshot(tmp_path, _base())
    with pytest.raises(RenameError, match="must not be empty"):
        rename_and_save(str(p), "", "httpx")


def test_rename_raises_on_missing_file():
    with pytest.raises(RenameError, match="not found"):
        rename_and_save("/nonexistent/snap.json", "a", "b")
