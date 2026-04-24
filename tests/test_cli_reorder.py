"""CLI integration tests for the reorder command."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> str:
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "3.0.0"},
            {"name": "click", "version": "8.1.0"},
        ],
        "npm": [],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_reorder_exits_zero(snapshot_file):
    with patch("sys.argv", ["stackfile", "reorder", "click", "0", "--input", snapshot_file]):
        assert main() == 0


def test_reorder_updates_file(snapshot_file):
    with patch("sys.argv", ["stackfile", "reorder", "click", "0", "--input", snapshot_file, "--section", "pip"]):
        main()
    saved = json.loads(Path(snapshot_file).read_text())
    assert saved["pip"][0]["name"] == "click"


def test_reorder_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    with patch("sys.argv", ["stackfile", "reorder", "flask", "0", "--input", snapshot_file, "--output", out]):
        assert main() == 0
    saved = json.loads(Path(out).read_text())
    assert saved["pip"][0]["name"] == "flask"


def test_reorder_nonzero_on_missing_file(tmp_path):
    missing = str(tmp_path / "nope.json")
    with patch("sys.argv", ["stackfile", "reorder", "requests", "0", "--input", missing]):
        assert main() != 0
