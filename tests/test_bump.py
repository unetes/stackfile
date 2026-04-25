"""Tests for stackfile.bump."""
import json
import pytest
from pathlib import Path

from stackfile.bump import _bump_version, bump_snapshot, BumpError


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _base():
    return {
        "version": 1,
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "3.1.2"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [
            {"name": "git", "version": "2.44.0"},
        ],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


# ---------------------------------------------------------------------------
# _bump_version unit tests
# ---------------------------------------------------------------------------

def test_bump_patch():
    assert _bump_version("2.28.0", "patch") == "2.28.1"


def test_bump_minor():
    assert _bump_version("2.28.0", "minor") == "2.29.0"


def test_bump_major():
    assert _bump_version("2.28.0", "major") == "3.0.0"


def test_bump_non_semver_returns_none():
    assert _bump_version("latest", "patch") is None


def test_bump_strips_caret():
    assert _bump_version("^1.2.3", "patch") == "1.2.4"


# ---------------------------------------------------------------------------
# bump_snapshot integration tests
# ---------------------------------------------------------------------------

def test_bump_all_sections_patch(tmp_path):
    path = write_snapshot(tmp_path)
    result = bump_snapshot(path, "patch")
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["version"] == "2.28.1"
    assert data["npm"][0]["version"] == "4.17.22"
    assert result["_bumped"] == 4


def test_bump_minor_resets_patch(tmp_path):
    path = write_snapshot(tmp_path)
    bump_snapshot(path, "minor")
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["version"] == "2.29.0"


def test_bump_specific_name_only(tmp_path):
    path = write_snapshot(tmp_path)
    result = bump_snapshot(path, "patch", name="requests")
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["version"] == "2.28.1"
    assert data["pip"][1]["version"] == "3.1.2"  # unchanged
    assert result["_bumped"] == 1


def test_bump_section_flag_limits_scope(tmp_path):
    path = write_snapshot(tmp_path)
    result = bump_snapshot(path, "patch", section="pip")
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["version"] == "2.28.1"
    assert data["npm"][0]["version"] == "4.17.21"  # unchanged
    assert result["_bumped"] == 2


def test_bump_writes_to_output_path(tmp_path):
    path = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    bump_snapshot(path, "minor", output_path=out)
    assert Path(out).exists()
    data = json.loads(Path(out).read_text())
    assert data["pip"][0]["version"] == "2.29.0"


def test_bump_missing_file_raises(tmp_path):
    with pytest.raises(BumpError, match="not found"):
        bump_snapshot(str(tmp_path / "missing.json"), "patch")


def test_bump_invalid_section_raises(tmp_path):
    path = write_snapshot(tmp_path)
    with pytest.raises(BumpError, match="Section"):
        bump_snapshot(path, "patch", section="conda")
