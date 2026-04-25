"""CLI integration tests for the split command."""

import json
from pathlib import Path

import pytest

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    data = {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "flask", "version": "3.0.0"}],
        "npm": [{"name": "express", "version": "4.18.0"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return p


def test_split_exits_zero(snapshot_file, tmp_path):
    out_dir = tmp_path / "split_out"
    rc = main(["split", str(snapshot_file), "--output-dir", str(out_dir)])
    assert rc == 0


def test_split_creates_output_directory(snapshot_file, tmp_path):
    out_dir = tmp_path / "split_out"
    main(["split", str(snapshot_file), "--output-dir", str(out_dir)])
    assert out_dir.is_dir()


def test_split_creates_one_file_per_section(snapshot_file, tmp_path):
    out_dir = tmp_path / "split_out"
    main(["split", str(snapshot_file), "--output-dir", str(out_dir)])
    files = list(out_dir.glob("*.json"))
    assert len(files) == 3


def test_split_section_flag_limits_output(snapshot_file, tmp_path):
    out_dir = tmp_path / "split_out"
    main(["split", str(snapshot_file), "--output-dir", str(out_dir), "--sections", "pip"])
    files = list(out_dir.glob("*.json"))
    assert len(files) == 1
    assert "pip" in files[0].name


def test_split_missing_input_exits_nonzero(tmp_path):
    out_dir = tmp_path / "split_out"
    rc = main(["split", str(tmp_path / "nope.json"), "--output-dir", str(out_dir)])
    assert rc != 0
