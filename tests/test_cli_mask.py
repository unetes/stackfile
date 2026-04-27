"""CLI integration tests for the 'mask' subcommand."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> str:
    data = {
        "version": "1.0",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_mask_exits_zero(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["mask", snapshot_file, "--output", out])
    assert rc == 0


def test_mask_creates_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["mask", snapshot_file, "--output", out])
    assert Path(out).exists()


def test_mask_all_versions_by_default(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["mask", snapshot_file, "--output", out])
    data = json.loads(Path(out).read_text())
    for pkg in data["pip"] + data["npm"] + data["brew"]:
        assert set(pkg["version"]) == {"*"}


def test_mask_pattern_flag_limits_scope(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["mask", snapshot_file, "--output", out, "--pattern", "requests"])
    data = json.loads(Path(out).read_text())
    assert set(data["pip"][0]["version"]) == {"*"}
    assert data["pip"][1]["version"] == "3.0.0"


def test_mask_section_flag(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["mask", snapshot_file, "--output", out, "--section", "pip"])
    data = json.loads(Path(out).read_text())
    assert data["npm"][0]["version"] == "4.17.21"


def test_mask_keep_flag(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["mask", snapshot_file, "--output", out, "--pattern", "requests", "--keep", "2"])
    data = json.loads(Path(out).read_text())
    assert data["pip"][0]["version"].endswith(".0")


def test_mask_default_input_is_stackfile(tmp_path, monkeypatch):
    data = {
        "version": "1.0",
        "created_at": "2024-01-01",
        "pip": [{"name": "six", "version": "1.16.0"}],
        "npm": [],
        "brew": [],
    }
    sf = tmp_path / "stackfile.json"
    sf.write_text(json.dumps(data))
    out = str(tmp_path / "out.json")
    monkeypatch.chdir(tmp_path)
    rc = main(["mask", "--output", out])
    assert rc == 0
