"""CLI integration tests for the export command."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from stackfile.cli import build_parser, main


SAMPLE = {
    "pip": {"numpy": "1.26.0"},
    "npm": {},
    "brew": {},
}


@pytest.fixture()
def snapshot_file(tmp_path):
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(SAMPLE))
    return str(p)


def test_export_shell_exit_zero(snapshot_file, tmp_path):
    out = str(tmp_path / "install.sh")
    with patch("sys.argv", ["stackfile", "export", "--input", snapshot_file, "--output", out, "--format", "shell"]):
        code = main()
    assert code == 0


def test_export_requirements_exit_zero(snapshot_file, tmp_path):
    out = str(tmp_path / "requirements.txt")
    with patch("sys.argv", ["stackfile", "export", "--input", snapshot_file, "--output", out, "--format", "requirements"]):
        code = main()
    assert code == 0


def test_export_creates_file(snapshot_file, tmp_path):
    out = str(tmp_path / "install.sh")
    with patch("sys.argv", ["stackfile", "export", "--input", snapshot_file, "--output", out, "--format", "shell"]):
        main()
    assert Path(out).exists()
    assert "pip install" in Path(out).read_text()
