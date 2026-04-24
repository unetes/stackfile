"""CLI integration tests for the patch command."""

import json
from pathlib import Path

import pytest

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    data = {
        "version": "1.0",
        "created_at": "2024-01-01",
        "pip": {"packages": [{"name": "requests", "version": "2.28.0"}, {"name": "flask", "version": "2.0.0"}]},
        "npm": {"packages": [{"name": "lodash", "version": "4.17.20"}]},
        "brew": {"packages": []},
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_patch_exits_zero(snapshot_file, tmp_path, capsys):
    out = str(tmp_path / "out.json")
    rc = main(["patch", snapshot_file, "pip", "requests=2.31.0", "--output", out])
    assert rc == 0


def test_patch_updates_package_version(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["patch", snapshot_file, "pip", "requests=2.31.0", "--output", out])
    data = json.loads(Path(out).read_text())
    pkgs = {p["name"]: p["version"] for p in data["pip"]["packages"]}
    assert pkgs["requests"] == "2.31.0"


def test_patch_multiple_packages(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["patch", snapshot_file, "pip", "requests=2.31.0", "flask=3.0.0", "--output", out])
    data = json.loads(Path(out).read_text())
    pkgs = {p["name"]: p["version"] for p in data["pip"]["packages"]}
    assert pkgs["requests"] == "2.31.0"
    assert pkgs["flask"] == "3.0.0"


def test_patch_default_input(snapshot_file, capsys):
    rc = main(["patch", snapshot_file, "npm", "lodash=4.17.21"])
    assert rc == 0
    data = json.loads(Path(snapshot_file).read_text())
    assert data["npm"]["packages"][0]["version"] == "4.17.21"


def test_patch_nonzero_on_missing_file(tmp_path):
    rc = main(["patch", str(tmp_path / "ghost.json"), "pip", "requests=1.0.0"])
    assert rc != 0
