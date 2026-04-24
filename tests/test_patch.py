"""Tests for stackfile.patch."""

import json
from pathlib import Path

import pytest

from stackfile.patch import PatchError, patch_snapshot, _patch_packages


def _base():
    return {
        "version": "1.0",
        "created_at": "2024-01-01",
        "pip": {"packages": [{"name": "requests", "version": "2.28.0"}, {"name": "flask", "version": "2.0.0"}]},
        "npm": {"packages": [{"name": "lodash", "version": "4.17.20"}]},
        "brew": {"packages": [{"name": "git", "version": "2.40.0"}]},
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_patch_packages_updates_version():
    packages = [{"name": "requests", "version": "2.28.0"}]
    updates = [{"name": "requests", "version": "2.31.0"}]
    result, count = _patch_packages(packages, updates)
    assert count == 1
    assert result[0]["version"] == "2.31.0"


def test_patch_packages_ignores_unknown():
    packages = [{"name": "requests", "version": "2.28.0"}]
    updates = [{"name": "nonexistent", "version": "9.9.9"}]
    result, count = _patch_packages(packages, updates)
    assert count == 0
    assert result[0]["version"] == "2.28.0"


def test_patch_packages_no_mutation_of_original():
    packages = [{"name": "flask", "version": "2.0.0"}]
    updates = [{"name": "flask", "version": "3.0.0"}]
    _patch_packages(packages, updates)
    assert packages[0]["version"] == "2.0.0"


def test_patch_snapshot_updates_pip(tmp_path):
    path = write_snapshot(tmp_path)
    patches = {"pip": [{"name": "requests", "version": "2.31.0"}]}
    result = patch_snapshot(path, patches)
    pkgs = {p["name"]: p["version"] for p in result["pip"]["packages"]}
    assert pkgs["requests"] == "2.31.0"
    assert pkgs["flask"] == "2.0.0"


def test_patch_snapshot_writes_to_output_file(tmp_path):
    path = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    patches = {"npm": [{"name": "lodash", "version": "4.17.21"}]}
    patch_snapshot(path, patches, output_path=out)
    data = json.loads(Path(out).read_text())
    assert data["npm"]["packages"][0]["version"] == "4.17.21"


def test_patch_snapshot_section_flag_limits_scope(tmp_path):
    path = write_snapshot(tmp_path)
    patches = {
        "pip": [{"name": "requests", "version": "9.9.9"}],
        "npm": [{"name": "lodash", "version": "9.9.9"}],
    }
    result = patch_snapshot(path, patches, section="pip")
    pip_ver = {p["name"]: p["version"] for p in result["pip"]["packages"]}
    npm_ver = {p["name"]: p["version"] for p in result["npm"]["packages"]}
    assert pip_ver["requests"] == "9.9.9"
    assert npm_ver["lodash"] == "4.17.20"  # unchanged


def test_patch_snapshot_missing_file_raises(tmp_path):
    with pytest.raises(PatchError, match="not found"):
        patch_snapshot(str(tmp_path / "missing.json"), {})


def test_patch_snapshot_overwrites_input_when_no_output(tmp_path):
    path = write_snapshot(tmp_path)
    patches = {"brew": [{"name": "git", "version": "2.41.0"}]}
    patch_snapshot(path, patches)
    data = json.loads(Path(path).read_text())
    assert data["brew"]["packages"][0]["version"] == "2.41.0"
