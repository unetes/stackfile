"""Tests for the snapshot module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from stackfile.snapshot import take_snapshot, capture_pip, capture_npm, capture_brew


PIP_OUTPUT = json.dumps([{"name": "requests", "version": "2.31.0"}])
NPM_OUTPUT = json.dumps({"dependencies": {"typescript": {"version": "5.0.0"}}})
BREW_OUTPUT = "git 2.44.0\ncurl 8.6.0\n"


def _mock_run(outputs: dict):
    """Return a side_effect function that maps first cmd token to output."""
    def side_effect(cmd, **kwargs):
        result = MagicMock()
        result.returncode = 0
        key = cmd[0] if cmd[0] != sys.executable else "pip"
        result.stdout = outputs.get(key, "")
        return result
    return side_effect


import sys


@patch("stackfile.snapshot.subprocess.run")
def test_capture_pip(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=PIP_OUTPUT, stderr="")
    packages = capture_pip()
    assert packages == [{"name": "requests", "version": "2.31.0"}]


@patch("stackfile.snapshot.subprocess.run")
def test_capture_npm(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=NPM_OUTPUT, stderr="")
    packages = capture_npm()
    assert packages == [{"name": "typescript", "version": "5.0.0"}]


@patch("stackfile.snapshot.subprocess.run")
def test_capture_brew(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=BREW_OUTPUT, stderr="")
    packages = capture_brew()
    assert {"name": "git", "version": "2.44.0"} in packages
    assert {"name": "curl", "version": "8.6.0"} in packages


@patch("stackfile.snapshot.capture_pip", return_value=[{"name": "flask", "version": "3.0.0"}])
@patch("stackfile.snapshot.capture_npm", side_effect=FileNotFoundError("npm not found"))
def test_take_snapshot_partial(mock_npm, mock_pip, tmp_path):
    out = tmp_path / "stackfile.json"
    snapshot = take_snapshot(tools=["pip", "npm"], output_path=str(out))

    assert "pip" in snapshot["dependencies"]
    assert "npm" not in snapshot["dependencies"]
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["version"] == "1"
    assert len(data["dependencies"]["pip"]) == 1


@patch("stackfile.snapshot.capture_pip", return_value=[])
def test_take_snapshot_unknown_tool(mock_pip, tmp_path):
    out = tmp_path / "stackfile.json"
    snapshot = take_snapshot(tools=["pip", "cargo"], output_path=str(out))
    assert "cargo" not in snapshot["dependencies"]
