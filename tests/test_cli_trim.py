"""CLI integration tests for the trim command."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.0.0"},
            {"name": "django", "version": "4.0.0"},
        ]},
        "npm": {"packages": [{"name": "lodash", "version": "4.17.21"}]},
        "brew": {"packages": []},
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_trim_exits_zero(snapshot_file):
    rc = main(["trim", snapshot_file, "--limit", "2"])
    assert rc == 0


def test_trim_reduces_packages(snapshot_file):
    main(["trim", snapshot_file, "--limit", "1"])
    data = json.loads(Path(snapshot_file).read_text())
    assert len(data["pip"]["packages"]) == 1


def test_trim_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "trimmed.json")
    rc = main(["trim", snapshot_file, "--limit", "1", "--output", out])
    assert rc == 0
    assert Path(out).exists()


def test_trim_section_flag(snapshot_file):
    main(["trim", snapshot_file, "--limit", "1", "--section", "pip"])
    data = json.loads(Path(snapshot_file).read_text())
    assert len(data["pip"]["packages"]) == 1
    assert len(data["npm"]["packages"]) == 1  # untouched


def test_trim_nonzero_on_missing_file(tmp_path):
    rc = main(["trim", str(tmp_path / "nope.json"), "--limit", "2"])
    assert rc != 0
