"""Tests for stackfile.validate."""
import json
import pytest
from pathlib import Path
from stackfile.validate import validate_snapshot, validate_or_exit, ValidationError


def write_snapshot(tmp_path, data, name="stack.json"):
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


VALID = {
    "version": "1",
    "created_at": "2024-01-01T00:00:00",
    "pip": {"packages": ["requests==2.31.0"]},
    "npm": {"packages": ["typescript@5.0.0"]},
}


def test_valid_snapshot_no_errors(tmp_path):
    path = write_snapshot(tmp_path, VALID)
    assert validate_snapshot(path) == []


def test_missing_version(tmp_path):
    data = {**VALID}
    del data["version"]
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("version" in e for e in errors)


def test_missing_created_at(tmp_path):
    data = {**VALID}
    del data["created_at"]
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("created_at" in e for e in errors)


def test_packages_not_list(tmp_path):
    data = {**VALID, "pip": {"packages": "requests"}}
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("pip.packages" in e for e in errors)


def test_package_not_string(tmp_path):
    data = {**VALID, "npm": {"packages": [123]}}
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("npm.packages[0]" in e for e in errors)


def test_section_not_object(tmp_path):
    data = {**VALID, "brew": ["git"]}
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("brew" in e for e in errors)


def test_unknown_key(tmp_path):
    data = {**VALID, "conda": {"packages": []}}
    path = write_snapshot(tmp_path, data)
    errors = validate_snapshot(path)
    assert any("conda" in e for e in errors)


def test_file_not_found():
    with pytest.raises(ValidationError, match="not found"):
        validate_snapshot("/nonexistent/path.json")


def test_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json {{{")
    with pytest.raises(ValidationError, match="Invalid JSON"):
        validate_snapshot(str(p))


def test_validate_or_exit_valid(tmp_path, capsys):
    path = write_snapshot(tmp_path, VALID)
    validate_or_exit(path)  # should not raise
    out = capsys.readouterr().out
    assert "valid" in out


def test_validate_or_exit_invalid(tmp_path):
    data = {**VALID}
    del data["version"]
    path = write_snapshot(tmp_path, data)
    with pytest.raises(SystemExit) as exc_info:
        validate_or_exit(path)
    assert exc_info.value.code == 1
