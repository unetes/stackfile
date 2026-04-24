"""CLI integration tests for the rollback command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.cli import main


@pytest.fixture()
def history_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    snap = tmp_path / "stack.json"
    snap.write_text(json.dumps({"version": 1, "pip": [{"name": "flask", "version": "3.0.0"}]}))
    return snap


def _write_history(history_file: Path, entries: list[dict]) -> None:
    history_file.write_text(json.dumps(entries))


def test_rollback_exits_zero(tmp_path: Path, history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "restored.json"
    rc = main([
        "rollback",
        "--index", "0",
        "--history", str(history_file),
        "--output", str(dest),
    ])
    assert rc == 0


def test_rollback_creates_output_file(tmp_path: Path, history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "restored.json"
    main([
        "rollback",
        "--index", "0",
        "--history", str(history_file),
        "--output", str(dest),
    ])
    assert dest.exists()


def test_rollback_json_flag(capsys, tmp_path: Path, history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "restored.json"
    main([
        "rollback",
        "--index", "0",
        "--history", str(history_file),
        "--output", str(dest),
        "--json",
    ])
    out = json.loads(capsys.readouterr().out)
    assert out["index"] == 0


def test_rollback_nonzero_on_empty_history(tmp_path: Path, history_file: Path) -> None:
    _write_history(history_file, [])
    dest = tmp_path / "restored.json"
    rc = main([
        "rollback",
        "--index", "0",
        "--history", str(history_file),
        "--output", str(dest),
    ])
    assert rc != 0


def test_rollback_nonzero_on_bad_index(tmp_path: Path, history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "restored.json"
    rc = main([
        "rollback",
        "--index", "99",
        "--history", str(history_file),
        "--output", str(dest),
    ])
    assert rc != 0
