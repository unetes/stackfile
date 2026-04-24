"""Tests for stackfile.group."""

import json
import pytest
from pathlib import Path

from stackfile.group import (
    GroupError,
    add_group,
    remove_group,
    list_groups,
    group_and_save,
    _load,
)


def _base():
    return {
        "version": "1",
        "pip": [{"name": "requests", "version": "2.31.0"}, {"name": "flask", "version": "3.0.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [],
    }


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_add_group_sets_label():
    data = _base()
    count = add_group(data, "pip", "requests", "networking")
    assert count == 1
    pkg = next(p for p in data["pip"] if p["name"] == "requests")
    assert pkg["group"] == "networking"


def test_add_group_no_match_returns_zero():
    data = _base()
    count = add_group(data, "pip", "nonexistent", "tools")
    assert count == 0


def test_remove_group_clears_label():
    data = _base()
    data["pip"][0]["group"] = "networking"
    count = remove_group(data, "pip", "requests")
    assert count == 1
    assert "group" not in data["pip"][0]


def test_remove_group_missing_label_returns_zero():
    data = _base()
    count = remove_group(data, "pip", "requests")
    assert count == 0


def test_list_groups_aggregates_across_sections():
    data = _base()
    data["pip"][0]["group"] = "networking"
    data["npm"][0]["group"] = "utils"
    groups = list_groups(data)
    assert "networking" in groups
    assert groups["networking"] == [{"section": "pip", "name": "requests"}]
    assert "utils" in groups
    assert groups["utils"] == [{"section": "npm", "name": "lodash"}]


def test_list_groups_empty_when_none_set():
    data = _base()
    assert list_groups(data) == {}


def test_group_and_save_writes_file(tmp_path):
    data = _base()
    path = write_snapshot(tmp_path, data)
    group_and_save(path, "pip", "flask", "web")
    loaded = json.loads(Path(path).read_text())
    pkg = next(p for p in loaded["pip"] if p["name"] == "flask")
    assert pkg["group"] == "web"


def test_group_and_save_to_output_file(tmp_path):
    data = _base()
    src = write_snapshot(tmp_path, data)
    out = str(tmp_path / "out.json")
    group_and_save(src, "pip", "requests", "networking", output_path=out)
    assert Path(out).exists()
    loaded = json.loads(Path(out).read_text())
    pkg = next(p for p in loaded["pip"] if p["name"] == "requests")
    assert pkg["group"] == "networking"


def test_group_and_save_remove_group(tmp_path):
    data = _base()
    data["pip"][0]["group"] = "old"
    path = write_snapshot(tmp_path, data)
    group_and_save(path, "pip", "requests", None)
    loaded = json.loads(Path(path).read_text())
    pkg = next(p for p in loaded["pip"] if p["name"] == "requests")
    assert "group" not in pkg


def test_load_raises_on_missing_file():
    with pytest.raises(GroupError, match="Snapshot not found"):
        _load("/nonexistent/path/snap.json")
