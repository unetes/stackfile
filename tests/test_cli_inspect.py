"""CLI integration tests for the inspect command."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "django", "version": "4.2.0"},
        ],
        "npm": [{"name": "express", "version": "4.18.0"}],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_inspect_exits_zero(snapshot_file):
    with patch("sys.argv", ["stackfile", "inspect", "requests", "--input", snapshot_file]):
        rc = main()
    assert rc == 0


def test_inspect_exits_zero_json_flag(snapshot_file, capsys):
    with patch("sys.argv", ["stackfile", "inspect", "requests", "--input", snapshot_file, "--json"]):
        rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed[0]["name"] == "requests"


def test_inspect_human_output(snapshot_file, capsys):
    with patch("sys.argv", ["stackfile", "inspect", "django", "--input", snapshot_file]):
        main()
    captured = capsys.readouterr()
    assert "django" in captured.out
    assert "4.2.0" in captured.out


def test_inspect_not_found_message(snapshot_file, capsys):
    with patch("sys.argv", ["stackfile", "inspect", "nonexistent", "--input", snapshot_file]):
        rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


def test_inspect_section_flag(snapshot_file, capsys):
    with patch("sys.argv", ["stackfile", "inspect", "requests", "--input", snapshot_file, "--section", "pip"]):
        rc = main()
    assert rc == 0


def test_inspect_default_input(tmp_path, monkeypatch, capsys):
    data = {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "flask", "version": "3.0.0"}],
        "npm": [],
        "brew": [],
    }
    snap = tmp_path / "stackfile.json"
    snap.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    with patch("sys.argv", ["stackfile", "inspect", "flask"]):
        rc = main()
    assert rc == 0
