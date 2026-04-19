"""CLI integration tests for the validate command."""
import json
import pytest
from stackfile.cli import build_parser, main


def write_snapshot(tmp_path, data):
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


VALID = {
    "version": "1",
    "created_at": "2024-01-01T00:00:00",
    "pip": {"packages": ["flask==3.0.0"]},
}


def test_validate_exits_zero_for_valid(tmp_path):
    path = write_snapshot(tmp_path, VALID)
    parser = build_parser()
    args = parser.parse_args(["validate", path])
    assert args.command == "validate"
    assert args.input == path


def test_validate_main_exits_zero(tmp_path, monkeypatch):
    path = write_snapshot(tmp_path, VALID)
    monkeypatch.setattr("sys.argv", ["stackfile", "validate", path])
    assert main() == 0


def test_validate_main_exits_one_on_invalid(tmp_path, monkeypatch):
    data = {**VALID}
    del data["version"]
    path = write_snapshot(tmp_path, data)
    monkeypatch.setattr("sys.argv", ["stackfile", "validate", path])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_validate_default_input(tmp_path, monkeypatch):
    path = write_snapshot(tmp_path, VALID)
    monkeypatch.chdir(tmp_path)
    # rename to default name
    import shutil
    shutil.copy(path, tmp_path / "stackfile.json")
    monkeypatch.setattr("sys.argv", ["stackfile", "validate"])
    assert main() == 0
