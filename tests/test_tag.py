"""Tests for stackfile/tag.py."""
import json
import pytest
from pathlib import Path
from stackfile.tag import add_tag, remove_tag, list_tags, tag_and_save, TagError


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snapshot.json"
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture
def snapshot_file(tmp_path):
    return write_snapshot(tmp_path, {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "tags": ["stable"],
        "pip": {"packages": []},
        "npm": {"packages": []},
        "brew": {"packages": []},
    })


def test_list_tags_returns_existing(snapshot_file):
    tags = list_tags(snapshot_file)
    assert tags == ["stable"]


def test_list_tags_empty_when_missing(tmp_path):
    p = write_snapshot(tmp_path, {"version": "1"})
    assert list_tags(p) == []


def test_add_tag_appends(snapshot_file):
    data = add_tag(snapshot_file, "v2")
    assert "v2" in data["tags"]
    assert "stable" in data["tags"]


def test_add_tag_persists_to_file(snapshot_file):
    add_tag(snapshot_file, "production")
    saved = json.loads(Path(snapshot_file).read_text())
    assert "production" in saved["tags"]


def test_add_tag_duplicate_raises(snapshot_file):
    with pytest.raises(TagError, match="already exists"):
        add_tag(snapshot_file, "stable")


def test_remove_tag_removes(snapshot_file):
    data = remove_tag(snapshot_file, "stable")
    assert "stable" not in data["tags"]


def test_remove_tag_missing_raises(snapshot_file):
    with pytest.raises(TagError, match="not found"):
        remove_tag(snapshot_file, "nonexistent")


def test_add_tag_writes_to_output_path(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    add_tag(snapshot_file, "new", output_path=out)
    saved = json.loads(Path(out).read_text())
    assert "new" in saved["tags"]
    # original unchanged
    original = json.loads(Path(snapshot_file).read_text())
    assert "new" not in original["tags"]


def test_tag_and_save_add(snapshot_file):
    data = tag_and_save("add", snapshot_file, "beta")
    assert "beta" in data["tags"]


def test_tag_and_save_remove(snapshot_file):
    data = tag_and_save("remove", snapshot_file, "stable")
    assert "stable" not in data["tags"]


def test_tag_and_save_invalid_action_raises(snapshot_file):
    with pytest.raises(TagError, match="Unknown action"):
        tag_and_save("rename", snapshot_file, "x")


def test_load_missing_file_raises():
    with pytest.raises(TagError, match="Cannot load"):
        list_tags("/nonexistent/snapshot.json")
