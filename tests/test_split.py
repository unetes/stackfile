"""Tests for stackfile.split."""

import json
from pathlib import Path

import pytest

from stackfile.split import SplitError, split_snapshot, split_and_save


def _base() -> dict:
    return {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [{"name": "jq", "version": "1.7"}],
    }


def write_snapshot(tmp_path: Path, data: dict | None = None) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return p


def test_split_returns_all_sections_by_default():
    result = split_snapshot(_base())
    assert set(result.keys()) == {"pip", "npm", "brew"}


def test_split_pip_section_has_only_pip_packages():
    result = split_snapshot(_base())
    assert result["pip"]["pip"] == [{"name": "requests", "version": "2.31.0"}]
    assert result["pip"]["npm"] == []
    assert result["pip"]["brew"] == []


def test_split_npm_section_isolated():
    result = split_snapshot(_base())
    assert result["npm"]["npm"] == [{"name": "lodash", "version": "4.17.21"}]
    assert result["npm"]["pip"] == []


def test_split_preserves_version_metadata():
    result = split_snapshot(_base())
    for section_data in result.values():
        assert section_data["version"] == "1.0"
        assert section_data["created_at"] == "2024-01-01T00:00:00"


def test_split_with_section_filter():
    result = split_snapshot(_base(), sections=["pip", "brew"])
    assert set(result.keys()) == {"pip", "brew"}
    assert "npm" not in result


def test_split_unknown_section_raises():
    with pytest.raises(SplitError, match="Unknown section"):
        split_snapshot(_base(), sections=["cargo"])


def test_split_and_save_creates_files(tmp_path):
    snap = write_snapshot(tmp_path)
    out_dir = tmp_path / "out"
    written = split_and_save(str(snap), str(out_dir))
    assert len(written) == 3
    for path in written.values():
        assert Path(path).exists()


def test_split_and_save_filenames_contain_section(tmp_path):
    snap = write_snapshot(tmp_path)
    out_dir = tmp_path / "out"
    written = split_and_save(str(snap), str(out_dir))
    for section, path in written.items():
        assert section in Path(path).name


def test_split_and_save_missing_file_raises(tmp_path):
    with pytest.raises(SplitError, match="not found"):
        split_and_save(str(tmp_path / "missing.json"), str(tmp_path / "out"))


def test_split_and_save_content_is_valid_json(tmp_path):
    snap = write_snapshot(tmp_path)
    out_dir = tmp_path / "out"
    written = split_and_save(str(snap), str(out_dir))
    for path in written.values():
        data = json.loads(Path(path).read_text())
        assert "version" in data
