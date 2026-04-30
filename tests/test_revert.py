"""Tests for stackfile.revert."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.revert import RevertError, revert_snapshot


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


def write_snapshot(tmp_path: Path, data: dict, name: str = "snap.json") -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def write_history(tmp_path: Path, entries: list[dict]) -> str:
    p = tmp_path / "history.json"
    p.write_text(json.dumps(entries))
    return str(p)


def test_revert_one_step(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    history = [
        {"snapshot_path": snap_path, "state": _older()},
        {"snapshot_path": snap_path, "state": _base()},
    ]
    hist_path = write_history(tmp_path, history)
    result = revert_snapshot(snap_path, hist_path, steps=1)
    assert result["pip"]["packages"][0]["version"] == "2.28.0"


def test_revert_two_steps(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    history = [
        {"snapshot_path": snap_path, "state": _older()},
        {"snapshot_path": snap_path, "state": _base()},
    ]
    hist_path = write_history(tmp_path, history)
    result = revert_snapshot(snap_path, hist_path, steps=2)
    assert result["pip"]["packages"][0]["version"] == "2.27.0"


def test_revert_writes_to_output(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    history = [{"snapshot_path": snap_path, "state": _older()}]
    hist_path = write_history(tmp_path, history)
    out_path = str(tmp_path / "out.json")
    revert_snapshot(snap_path, hist_path, steps=1, output=out_path)
    data = json.loads(Path(out_path).read_text())
    assert data["pip"]["packages"][0]["version"] == "2.27.0"


def test_revert_empty_history_raises(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    hist_path = write_history(tmp_path, [])
    with pytest.raises(RevertError, match="No history"):
        revert_snapshot(snap_path, hist_path)


def test_revert_insufficient_steps_raises(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    history = [{"snapshot_path": snap_path, "state": _older()}]
    hist_path = write_history(tmp_path, history)
    with pytest.raises(RevertError, match="Not enough history"):
        revert_snapshot(snap_path, hist_path, steps=5)


def test_revert_invalid_steps_raises(tmp_path):
    snap_path = write_snapshot(tmp_path, _base())
    hist_path = write_history(tmp_path, [])
    with pytest.raises(RevertError, match="steps must be"):
        revert_snapshot(snap_path, hist_path, steps=0)


def test_revert_missing_snapshot_raises(tmp_path):
    hist_path = write_history(tmp_path, [])
    with pytest.raises(RevertError, match="File not found"):
        revert_snapshot(str(tmp_path / "ghost.json"), str(hist_path))
