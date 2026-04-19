"""Tests for the CLI entry point."""
from unittest.mock import patch, call
import pytest
from stackfile.cli import main, build_parser


def test_no_command_returns_nonzero():
    assert main([]) == 1


def test_snapshot_default_output(tmp_path):
    output = str(tmp_path / "stackfile.json")
    with patch("stackfile.cli.take_snapshot") as mock_snap:
        result = main(["snapshot", "--output", output])
    mock_snap.assert_called_once_with(output=output, skip=set())
    assert result == 0


def test_snapshot_with_skip_flags(tmp_path):
    output = str(tmp_path / "stackfile.json")
    with patch("stackfile.cli.take_snapshot") as mock_snap:
        main(["snapshot", "--output", output, "--no-pip", "--no-brew"])
    _, kwargs = mock_snap.call_args
    assert kwargs["skip"] == {"pip", "brew"}


def test_restore_default_input():
    with patch("stackfile.cli.restore_snapshot") as mock_restore:
        result = main(["restore"])
    mock_restore.assert_called_once_with(input_file="stackfile.json", skip=set())
    assert result == 0


def test_restore_custom_input(tmp_path):
    snap_file = str(tmp_path / "my_snap.json")
    with patch("stackfile.cli.restore_snapshot") as mock_restore:
        result = main(["restore", snap_file])
    mock_restore.assert_called_once_with(input_file=snap_file, skip=set())
    assert result == 0


def test_restore_with_skip_flags():
    with patch("stackfile.cli.restore_snapshot") as mock_restore:
        main(["restore", "--no-npm"])
    _, kwargs = mock_restore.call_args
    assert kwargs["skip"] == {"npm"}


def test_build_parser_snapshot_defaults():
    parser = build_parser()
    args = parser.parse_args(["snapshot"])
    assert args.output == "stackfile.json"
    assert not args.no_pip
    assert not args.no_npm
    assert not args.no_brew


def test_build_parser_restore_defaults():
    parser = build_parser()
    args = parser.parse_args(["restore"])
    assert args.input == "stackfile.json"
    assert not args.no_pip
    assert not args.no_npm
    assert not args.no_brew
