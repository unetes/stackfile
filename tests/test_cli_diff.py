"""Tests for the `diff` subcommand in the CLI."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from stackfile.cli import main


@pytest.fixture
def two_snapshots(tmp_path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps({
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [],
        "brew": [],
    }))
    new.write_text(json.dumps({
        "pip": [{"name": "requests", "version": "2.31.0"}, {"name": "click", "version": "8.0.0"}],
        "npm": [],
        "brew": [],
    }))
    return str(old), str(new)


def test_diff_command_exits_zero(two_snapshots):
    old, new = two_snapshots
    assert main(["diff", old, new]) == 0


def test_diff_command_json_flag(two_snapshots, capsys):
    old, new = two_snapshots
    main(["diff", old, new, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "pip" in data


def test_diff_command_human_output(two_snapshots, capsys):
    old, new = two_snapshots
    main(["diff", old, new])
    captured = capsys.readouterr()
    assert "+" in captured.out or "~" in captured.out


def test_diff_identical_snapshots(two_snapshots, capsys):
    old, _ = two_snapshots
    main(["diff", old, old])
    captured = capsys.readouterr()
    assert "No differences found." in captured.out
