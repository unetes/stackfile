"""Tests for stackfile.rollback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.rollback import (
    RollbackError,
    list_rollback_points,
    rollback_to,
    rollback_and_print,
)


@pytest.fixture()
def history_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    snap = tmp_path / "stack.json"
    snap.write_text(json.dumps({"version": 1, "pip": [{"name": "requests", "version": "2.31.0"}]}))
    return snap


def _write_history(history_file: Path, entries: list[dict]) -> None:
    history_file.write_text(json.dumps(entries))


def test_list_rollback_points_empty_when_no_history(history_file: Path) -> None:
    history_file.write_text(json.dumps([]))
    assert list_rollback_points(history_file) == []


def test_list_rollback_points_filters_missing_path(history_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": None}])
    assert list_rollback_points(history_file) == []


def test_list_rollback_points_returns_entries_with_path(history_file: Path, snapshot_file: Path) -> None:
    entry = {"event": "snapshot", "snapshot_path": str(snapshot_file)}
    _write_history(history_file, [entry])
    points = list_rollback_points(history_file)
    assert len(points) == 1
    assert points[0]["snapshot_path"] == str(snapshot_file)


def test_rollback_to_restores_file(tmp_path: Path, history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "restored.json"
    result = rollback_to(0, history_file, output=dest)
    assert result == dest
    assert dest.exists()
    data = json.loads(dest.read_text())
    assert data["version"] == 1


def test_rollback_to_raises_on_empty_history(history_file: Path) -> None:
    _write_history(history_file, [])
    with pytest.raises(RollbackError, match="No rollback points"):
        rollback_to(0, history_file)


def test_rollback_to_raises_on_out_of_range(history_file: Path, snapshot_file: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    with pytest.raises(RollbackError, match="out of range"):
        rollback_to(5, history_file)


def test_rollback_to_raises_when_snapshot_missing(history_file: Path, tmp_path: Path) -> None:
    ghost = tmp_path / "ghost.json"
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(ghost)}])
    with pytest.raises(RollbackError, match="not found"):
        rollback_to(0, history_file)


def test_rollback_and_print_json(capsys, history_file: Path, snapshot_file: Path, tmp_path: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "out.json"
    rollback_and_print(0, history_file, output=dest, as_json=True)
    out = json.loads(capsys.readouterr().out)
    assert out["index"] == 0
    assert "restored" in out


def test_rollback_and_print_human(capsys, history_file: Path, snapshot_file: Path, tmp_path: Path) -> None:
    _write_history(history_file, [{"event": "snapshot", "snapshot_path": str(snapshot_file)}])
    dest = tmp_path / "out.json"
    rollback_and_print(0, history_file, output=dest, as_json=False)
    out = capsys.readouterr().out
    assert "Rolled back" in out
