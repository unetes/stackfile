"""CLI integration tests for the normalize command."""

import json
import pytest
from pathlib import Path

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "My_Package", "version": "v1.0.0"},
            {"name": "another.lib", "version": "=2.3.4"},
        ],
        "npm": [{"name": "SomeLib", "version": "v0.5.0"}],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_normalize_exits_zero(snapshot_file):
    rc = main(["normalize", snapshot_file])
    assert rc == 0


def test_normalize_updates_file(snapshot_file):
    main(["normalize", snapshot_file])
    data = json.loads(Path(snapshot_file).read_text())
    names = [p["name"] for p in data["pip"]]
    assert "my-package" in names
    assert "another-lib" in names


def test_normalize_strips_version_prefix(snapshot_file):
    main(["normalize", snapshot_file])
    data = json.loads(Path(snapshot_file).read_text())
    versions = [p["version"] for p in data["pip"]]
    assert "1.0.0" in versions
    assert "2.3.4" in versions


def test_normalize_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "normalized.json")
    rc = main(["normalize", snapshot_file, "--output", out])
    assert rc == 0
    assert Path(out).exists()


def test_normalize_section_flag(snapshot_file):
    main(["normalize", snapshot_file, "--section", "pip"])
    data = json.loads(Path(snapshot_file).read_text())
    # npm should be untouched
    assert data["npm"][0]["name"] == "SomeLib"
