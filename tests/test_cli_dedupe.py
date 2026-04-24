"""CLI integration tests for the dedupe command."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {
            "packages": [
                {"name": "requests", "version": "2.0"},
                {"name": "requests", "version": "2.31"},
                {"name": "flask", "version": "3.0"},
            ]
        },
        "npm": {"packages": []},
        "brew": {"packages": []},
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_dedupe_exits_zero(snapshot_file):
    assert main(["dedupe", snapshot_file]) == 0


def test_dedupe_removes_duplicates(snapshot_file):
    main(["dedupe", snapshot_file])
    data = json.loads(Path(snapshot_file).read_text())
    assert len(data["pip"]["packages"]) == 2


def test_dedupe_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "deduped.json")
    assert main(["dedupe", snapshot_file, "--output", out]) == 0
    assert Path(out).exists()


def test_dedupe_section_flag(snapshot_file):
    result = main(["dedupe", snapshot_file, "--section", "pip"])
    assert result == 0
