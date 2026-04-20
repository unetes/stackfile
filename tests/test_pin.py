"""Tests for stackfile.pin module."""

import json
import pytest
from pathlib import Path
from stackfile.pin import pin_snapshot, PinError, _pin_packages


@pytest.fixture
def write_snapshot(tmp_path):
    def _write(data, filename="stack.json"):
        p = tmp_path / filename
        p.write_text(json.dumps(data))
        return str(p)
    return _write


VALID_SNAPSHOT = {
    "version": 1,
    "created_at": "2024-01-01T00:00:00+00:00",
    "pip": [{"name": "requests", "version": "2.31.0"}],
    "npm": [{"name": "typescript", "version": "5.4.2"}],
    "brew": [{"name": "git", "version": "2.44.0"}],
}


def test_pin_valid_snapshot_returns_dict(write_snapshot, tmp_path):
    src = write_snapshot(VALID_SNAPSHOT)
    out_path = str(tmp_path / "pinned.json")
    result = pin_snapshot(src, out_path)
    assert result["pinned"] is True
    assert result["pip"] == [{"name": "requests", "version": "2.31.0"}]


def test_pin_writes_output_file(write_snapshot, tmp_path):
    src = write_snapshot(VALID_SNAPSHOT)
    out_path = str(tmp_path / "pinned.json")
    pin_snapshot(src, out_path)
    data = json.loads(Path(out_path).read_text())
    assert data["pinned"] is True
    assert len(data["brew"]) == 1


def test_pin_overwrites_input_when_no_output(write_snapshot):
    src = write_snapshot(VALID_SNAPSHOT)
    pin_snapshot(src)
    data = json.loads(Path(src).read_text())
    assert data["pinned"] is True


def test_pin_raises_on_wildcard_version():
    packages = [{"name": "flask", "version": "*"}]
    with pytest.raises(PinError, match="flask"):
        _pin_packages(packages)


def test_pin_raises_on_latest_version():
    packages = [{"name": "lodash", "version": "latest"}]
    with pytest.raises(PinError, match="lodash"):
        _pin_packages(packages)


def test_pin_raises_on_empty_version():
    packages = [{"name": "cowsay", "version": ""}]
    with pytest.raises(PinError, match="cowsay"):
        _pin_packages(packages)


def test_pin_preserves_all_sections(write_snapshot, tmp_path):
    src = write_snapshot(VALID_SNAPSHOT)
    out_path = str(tmp_path / "pinned.json")
    result = pin_snapshot(src, out_path)
    assert len(result["pip"]) == 1
    assert len(result["npm"]) == 1
    assert len(result["brew"]) == 1


def test_pin_empty_sections(write_snapshot, tmp_path):
    snapshot = {"version": 1, "created_at": "2024-01-01T00:00:00+00:00",
                "pip": [], "npm": [], "brew": []}
    src = write_snapshot(snapshot)
    out_path = str(tmp_path / "pinned.json")
    result = pin_snapshot(src, out_path)
    assert result["pip"] == []
    assert result["npm"] == []
    assert result["brew"] == []
