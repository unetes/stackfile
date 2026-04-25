"""CLI integration tests for the archive command."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stackfile.cli import main


_base = {
    "version": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "pip": [{"name": "flask", "version": "3.0.0"}],
    "npm": [],
    "brew": [],
}


@pytest.fixture
def snapshot_file(tmp_path):
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(_base))
    return str(p)


@pytest.fixture
def archive_dir(tmp_path):
    return str(tmp_path / "archives")


def test_archive_exits_zero(snapshot_file, archive_dir):
    rc = main(["archive", "--input", snapshot_file, "--dir", archive_dir])
    assert rc == 0


def test_archive_creates_file_in_dir(snapshot_file, archive_dir):
    main(["archive", "--input", snapshot_file, "--dir", archive_dir])
    files = list(Path(archive_dir).glob("*.json"))
    assert len(files) == 1


def test_archive_list_exits_zero(snapshot_file, archive_dir):
    main(["archive", "--input", snapshot_file, "--dir", archive_dir])
    rc = main(["archive", "--list", "--dir", archive_dir])
    assert rc == 0


def test_archive_list_shows_filename(snapshot_file, archive_dir, capsys):
    main(["archive", "--input", snapshot_file, "--dir", archive_dir])
    main(["archive", "--list", "--dir", archive_dir])
    captured = capsys.readouterr()
    assert "stack." in captured.out


def test_archive_default_input(tmp_path, archive_dir):
    default = tmp_path / "stackfile.json"
    default.write_text(json.dumps(_base))
    rc = main(["archive", "--input", str(default), "--dir", archive_dir])
    assert rc == 0
