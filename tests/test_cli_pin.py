"""CLI integration tests for the `stackfile pin` command."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": 1,
        "created_at": "2024-01-01T00:00:00+00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [{"name": "typescript", "version": "5.4.2"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    }
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_pin_exits_zero(snapshot_file, tmp_path, capsys):
    out = str(tmp_path / "pinned.json")
    rc = main(["pin", "--input", snapshot_file, "--output", out])
    assert rc == 0


def test_pin_creates_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "pinned.json")
    main(["pin", "--input", snapshot_file, "--output", out])
    assert Path(out).exists()


def test_pin_output_has_pinned_flag(snapshot_file, tmp_path):
    out = str(tmp_path / "pinned.json")
    main(["pin", "--input", snapshot_file, "--output", out])
    data = json.loads(Path(out).read_text())
    assert data.get("pinned") is True


def test_pin_default_input(tmp_path, monkeypatch):
    data = {
        "version": 1,
        "created_at": "2024-01-01T00:00:00+00:00",
        "pip": [{"name": "flask", "version": "3.0.0"}],
        "npm": [],
        "brew": [],
    }
    default = tmp_path / "stack.json"
    default.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    out = str(tmp_path / "pinned.json")
    rc = main(["pin", "--output", out])
    assert rc == 0
    result = json.loads(Path(out).read_text())
    assert result["pinned"] is True
