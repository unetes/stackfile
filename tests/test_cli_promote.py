"""CLI integration tests for the promote command."""

import json
import pytest
from pathlib import Path

from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": 1,
        "pip": [
            {"name": "requests", "version": "2.28.0"},
            {"name": "flask", "version": "2.0.0"},
        ],
        "npm": [
            {"name": "lodash", "version": "4.17.21"},
        ],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_promote_exits_zero(snapshot_file):
    rc = main(["promote", "requests", "--from", "pip", "--to", "npm",
               "--input", snapshot_file])
    assert rc == 0


def test_promote_updates_file(snapshot_file):
    main(["promote", "flask", "--from", "pip", "--to", "npm",
          "--input", snapshot_file])
    result = json.loads(Path(snapshot_file).read_text())
    assert not any(p["name"] == "flask" for p in result["pip"])
    assert any(p["name"] == "flask" for p in result["npm"])


def test_promote_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["promote", "requests", "--from", "pip", "--to", "npm",
               "--input", snapshot_file, "--output", out])
    assert rc == 0
    assert Path(out).exists()
    result = json.loads(Path(out).read_text())
    assert any(p["name"] == "requests" for p in result["npm"])


def test_promote_nonzero_on_missing_file(tmp_path):
    rc = main(["promote", "requests", "--from", "pip", "--to", "npm",
               "--input", str(tmp_path / "missing.json")])
    assert rc != 0


def test_promote_no_match_exits_zero(snapshot_file):
    rc = main(["promote", "nonexistent", "--from", "pip", "--to", "npm",
               "--input", snapshot_file])
    assert rc == 0
