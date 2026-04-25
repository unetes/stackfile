"""Tests for stackfile.archive."""

import json
import pytest
from pathlib import Path

from stackfile.archive import (
    ArchiveError,
    archive_snapshot,
    list_archives,
    restore_archive,
)


def _write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


_base = {
    "version": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "pip": [{"name": "requests", "version": "2.31.0"}],
    "npm": [],
    "brew": [],
}


@pytest.fixture
def snapshot_file(tmp_path):
    p = tmp_path / "stack.json"
    _write(p, _base)
    return str(p)


def test_archive_creates_file(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    result = archive_snapshot(snapshot_file, archive_dir)
    assert Path(result).exists()


def test_archive_filename_contains_stem(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    result = archive_snapshot(snapshot_file, archive_dir)
    assert Path(result).name.startswith("stack.")


def test_archive_filename_contains_timestamp(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    result = archive_snapshot(snapshot_file, archive_dir)
    # timestamp portion matches YYYYMMDDTHHMMSSz pattern
    parts = Path(result).stem.split(".")
    assert len(parts) == 2
    assert parts[1].endswith("Z")


def test_archive_content_matches_original(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    result = archive_snapshot(snapshot_file, archive_dir)
    with open(result) as f:
        data = json.load(f)
    assert data["pip"][0]["name"] == "requests"


def test_archive_missing_file_raises(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        archive_snapshot(str(tmp_path / "missing.json"), str(tmp_path / "arch"))


def test_list_archives_empty_when_no_dir(tmp_path):
    result = list_archives(str(tmp_path / "nodir"))
    assert result == []


def test_list_archives_returns_created_archive(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    archive_snapshot(snapshot_file, archive_dir)
    results = list_archives(archive_dir)
    assert len(results) == 1


def test_list_archives_filters_by_stem(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    archive_snapshot(snapshot_file, archive_dir)
    # filter with matching stem
    results = list_archives(archive_dir, stem="stack.")
    assert len(results) == 1
    # filter with non-matching stem
    results_none = list_archives(archive_dir, stem="other.")
    assert results_none == []


def test_restore_archive_copies_to_dest(tmp_path, snapshot_file):
    archive_dir = str(tmp_path / "archives")
    archived = archive_snapshot(snapshot_file, archive_dir)
    dest = str(tmp_path / "restored.json")
    restore_archive(archived, dest)
    assert Path(dest).exists()
    with open(dest) as f:
        data = json.load(f)
    assert data["version"] == 1


def test_restore_archive_invalid_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(ArchiveError):
        restore_archive(str(bad), str(tmp_path / "out.json"))
