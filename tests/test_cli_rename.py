"""CLI integration tests for the rename command."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_rename_exits_zero(snapshot_file, capsys):
    rc = main(["rename", "requests", "httpx", "--input", snapshot_file])
    assert rc == 0


def test_rename_updates_file(snapshot_file):
    main(["rename", "requests", "httpx", "--input", snapshot_file])
    result = json.loads(Path(snapshot_file).read_text())
    names = [p["name"] for p in result["pip"]]
    assert "httpx" in names
    assert "requests" not in names


def test_rename_with_section_flag(snapshot_file):
    main(["rename", "requests", "httpx", "--input", snapshot_file, "--section", "pip"])
    result = json.loads(Path(snapshot_file).read_text())
    assert result["pip"][0]["name"] == "httpx"


def test_rename_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["rename", "requests", "httpx", "--input", snapshot_file, "--output", out])
    assert rc == 0
    result = json.loads(Path(out).read_text())
    assert result["pip"][0]["name"] == "httpx"


def test_rename_no_match_exits_zero_with_message(snapshot_file, capsys):
    rc = main(["rename", "nonexistent", "other", "--input", snapshot_file])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0" in out or "renamed" in out.lower()
