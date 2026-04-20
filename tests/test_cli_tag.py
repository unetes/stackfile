"""CLI integration tests for the tag command."""
import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "tags": ["stable"],
        "pip": {"packages": []},
        "npm": {"packages": []},
        "brew": {"packages": []},
    }
    p = tmp_path / "snapshot.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_tag_add_exits_zero(snapshot_file):
    rc = main(["tag", "add", "v2", "--input", snapshot_file])
    assert rc == 0


def test_tag_remove_exits_zero(snapshot_file):
    rc = main(["tag", "remove", "stable", "--input", snapshot_file])
    assert rc == 0


def test_tag_list_exits_zero(snapshot_file):
    rc = main(["tag", "list", "--input", snapshot_file])
    assert rc == 0


def test_tag_add_persists(snapshot_file):
    main(["tag", "add", "production", "--input", snapshot_file])
    saved = json.loads(Path(snapshot_file).read_text())
    assert "production" in saved["tags"]


def test_tag_add_with_output(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["tag", "add", "release", "--input", snapshot_file, "--output", out])
    assert rc == 0
    assert Path(out).exists()
    saved = json.loads(Path(out).read_text())
    assert "release" in saved["tags"]


def test_tag_duplicate_exits_nonzero(snapshot_file):
    rc = main(["tag", "add", "stable", "--input", snapshot_file])
    assert rc != 0


def test_tag_remove_missing_exits_nonzero(snapshot_file):
    rc = main(["tag", "remove", "ghost", "--input", snapshot_file])
    assert rc != 0
