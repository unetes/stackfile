"""CLI integration tests for the compact subcommand."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "bare-pkg", "version": ""},
        ],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [{"name": "bare-brew", "version": ""}],
    }


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(_base()))
    return p


def test_compact_exits_zero(snapshot_file, capsys):
    rc = main(["compact", str(snapshot_file)])
    assert rc == 0


def test_compact_removes_bare_packages(snapshot_file):
    main(["compact", str(snapshot_file)])
    data = json.loads(snapshot_file.read_text())
    names = [p["name"] for p in data["pip"]]
    assert "bare-pkg" not in names
    assert "requests" in names


def test_compact_to_output_file(snapshot_file, tmp_path):
    out = tmp_path / "out.json"
    rc = main(["compact", str(snapshot_file), "--output", str(out)])
    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "pip" in data


def test_compact_dry_run_does_not_modify(snapshot_file):
    original = snapshot_file.read_text()
    main(["compact", str(snapshot_file), "--dry-run"])
    assert snapshot_file.read_text() == original


def test_compact_section_flag(snapshot_file):
    main(["compact", str(snapshot_file), "--section", "pip"])
    data = json.loads(snapshot_file.read_text())
    # brew bare-brew should still be present (not compacted)
    names = [p["name"] for p in data["brew"]]
    assert "bare-brew" in names


def test_compact_prints_removed_count(snapshot_file, capsys):
    main(["compact", str(snapshot_file)])
    captured = capsys.readouterr()
    assert "removed" in captured.out.lower() or "2" in captured.out
