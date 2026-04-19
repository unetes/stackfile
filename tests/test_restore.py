"""Tests for stackfile.restore module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, call

from stackfile.restore import restore_pip, restore_npm, restore_brew, restore_snapshot


PIP_PACKAGES = [{"name": "requests", "version": "2.31.0"}]
NPM_PACKAGES = [{"name": "typescript", "version": "5.0.0"}]
BREW_PACKAGES = [{"name": "git", "version": "2.40.0"}]


@patch("stackfile.restore._run")
def test_restore_pip(mock_run):
    restore_pip(PIP_PACKAGES)
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "pip" in args
    assert "requests==2.31.0" in args


@patch("stackfile.restore._run")
def test_restore_npm(mock_run):
    restore_npm(NPM_PACKAGES)
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "npm" in args
    assert "typescript@5.0.0" in args


@patch("stackfile.restore._run")
def test_restore_brew(mock_run):
    restore_brew(BREW_PACKAGES)
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "brew" in args
    assert "git" in args


@patch("stackfile.restore._run")
def test_restore_empty_packages(mock_run):
    restore_pip([])
    restore_npm([])
    restore_brew([])
    mock_run.assert_not_called()


@patch("stackfile.restore.restore_pip")
@patch("stackfile.restore.restore_npm")
@patch("stackfile.restore.restore_brew")
def test_restore_snapshot(mock_brew, mock_npm, mock_pip, tmp_path):
    snapshot = {
        "created_at": "2024-01-01T00:00:00",
        "pip": PIP_PACKAGES,
        "npm": NPM_PACKAGES,
        "brew": BREW_PACKAGES,
    }
    snapshot_file = tmp_path / "stackfile.json"
    snapshot_file.write_text(json.dumps(snapshot))

    restore_snapshot(str(snapshot_file))

    mock_pip.assert_called_once_with(PIP_PACKAGES)
    mock_npm.assert_called_once_with(NPM_PACKAGES)
    mock_brew.assert_called_once_with(BREW_PACKAGES)


def test_restore_snapshot_missing_file():
    with pytest.raises(FileNotFoundError, match="Snapshot file not found"):
        restore_snapshot("/nonexistent/stackfile.json")
