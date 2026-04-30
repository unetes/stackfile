"""CLI integration tests for the revert command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.cli import main


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": [{"name": "requests", "version": "2.28.0"}]},
        "npm": {"packages": []},
        "brew": {"packages": []},
    }


def _older() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": [{"name": "requests", "version": "2.27.0"}]},
        "npm": {"packages": []},
        "brew": {"packages": []},
    }


@pytest.fixture()
def snapshot_file(tmp_path):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(_base()))
    return str(p)


@pytest.fixture()
def history_file(tmp_path, snapshot_file):
    entries = [
        {"snapshot_path": snapshot_file, "state": _older()},
        {"snapshot_path": snapshot_file, "state": _base()},
    ]
    p = tmp_path / "history.json"
    p.write_text(json.dumps(entries))
    return str(p)


def test_revert_exits_zero(snapshot_file, history_file):
    rc = main(["revert", "--input", snapshot_file, "--history", history_file])
    assert rc == 0


def test_revert_updates_file(snapshot_file, history_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["revert", "--input", snapshot_file, "--history", history_file,
          "--steps", "2", "--output", out])
    data = json.loads(Path(out).read_text())
    assert data["pip"]["packages"][0]["version"] == "2.27.0"


def test_revert_json_flag(snapshot_file, history_file, capsys):
    main(["revert", "--input", snapshot_file, "--history", history_file,
          "--json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "pip" in parsed


def test_revert_nonzero_on_missing_file(tmp_path):
    rc = main(["revert", "--input", str(tmp_path / "ghost.json"),
               "--history", str(tmp_path / "hist.json")])
    assert rc != 0


def test_revert_human_output_message(snapshot_file, history_file, capsys):
    main(["revert", "--input", snapshot_file, "--history", history_file])
    out = capsys.readouterr().out
    assert "Reverted" in out
