"""CLI integration tests for the `strip` subcommand."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "description": "env",
        "pinned": True,
        "tags": ["ci"],
        "pip": [{"name": "flask", "version": "3.0.0", "note": "web fw"}],
        "npm": [],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return p


def test_strip_exits_zero(snapshot_file, capsys):
    rc = main(["strip", str(snapshot_file)])
    assert rc == 0


def test_strip_removes_metadata(snapshot_file):
    main(["strip", str(snapshot_file)])
    result = json.loads(snapshot_file.read_text())
    assert "created_at" not in result
    assert "tags" not in result
    assert "pinned" not in result


def test_strip_to_output_file(snapshot_file, tmp_path):
    out = tmp_path / "clean.json"
    rc = main(["strip", str(snapshot_file), "--output", str(out)])
    assert rc == 0
    assert out.exists()
    result = json.loads(out.read_text())
    assert "description" not in result


def test_strip_notes_flag(snapshot_file):
    main(["strip", str(snapshot_file), "--strip-notes"])
    result = json.loads(snapshot_file.read_text())
    for pkg in result.get("pip", []):
        assert "note" not in pkg


def test_strip_keep_flag_preserves_field(snapshot_file):
    main(["strip", str(snapshot_file), "--keep", "description"])
    result = json.loads(snapshot_file.read_text())
    assert "description" in result
    # other defaults still stripped
    assert "tags" not in result


def test_strip_default_input_reads_stackfile(tmp_path, monkeypatch):
    data = {
        "version": "1",
        "created_at": "2024-06-01",
        "pip": [],
        "npm": [],
        "brew": [],
    }
    sf = tmp_path / "stackfile.json"
    sf.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    rc = main(["strip"])
    assert rc == 0
    result = json.loads(sf.read_text())
    assert "created_at" not in result
