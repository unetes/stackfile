"""CLI integration tests for the annotate command."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_annotate_exits_zero(snapshot_file):
    rc = main(["annotate", "requests", "--note", "my note", "--input", snapshot_file])
    assert rc == 0


def test_annotate_persists_note(snapshot_file):
    main(["annotate", "requests", "--note", "important", "--input", snapshot_file])
    data = json.loads(Path(snapshot_file).read_text())
    assert data["pip"][0]["note"] == "important"


def test_annotate_clear_removes_note(snapshot_file):
    data = json.loads(Path(snapshot_file).read_text())
    data["pip"][0]["note"] = "to remove"
    Path(snapshot_file).write_text(json.dumps(data))
    rc = main(["annotate", "requests", "--clear", "--input", snapshot_file])
    assert rc == 0
    saved = json.loads(Path(snapshot_file).read_text())
    assert "note" not in saved["pip"][0]


def test_annotate_to_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["annotate", "lodash", "--note", "util", "--input", snapshot_file, "--output", out])
    assert rc == 0
    saved = json.loads(Path(out).read_text())
    assert saved["npm"][0]["note"] == "util"


def test_annotate_with_section_flag(snapshot_file):
    rc = main(["annotate", "requests", "--note", "pip-only", "--section", "pip", "--input", snapshot_file])
    assert rc == 0
    data = json.loads(Path(snapshot_file).read_text())
    assert data["pip"][0]["note"] == "pip-only"
