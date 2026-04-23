"""Tests for stackfile.annotate."""

import json
import pytest
from pathlib import Path
from stackfile.annotate import (
    annotate_package,
    annotate_and_save,
    AnnotateError,
)


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_annotate_adds_note(tmp_path):
    data = _base()
    count = annotate_package(data, "requests", "used for HTTP calls")
    assert count == 1
    assert data["pip"][0]["note"] == "used for HTTP calls"


def test_annotate_updates_existing_note(tmp_path):
    data = _base()
    data["pip"][0]["note"] = "old note"
    annotate_package(data, "requests", "new note")
    assert data["pip"][0]["note"] == "new note"


def test_annotate_clears_note_when_none(tmp_path):
    data = _base()
    data["pip"][0]["note"] = "remove me"
    count = annotate_package(data, "requests", None)
    assert count == 1
    assert "note" not in data["pip"][0]


def test_annotate_no_match_returns_zero(tmp_path):
    data = _base()
    count = annotate_package(data, "nonexistent", "note")
    assert count == 0


def test_annotate_section_filter(tmp_path):
    data = _base()
    count = annotate_package(data, "requests", "pip only", section="npm")
    assert count == 0
    assert "note" not in data["pip"][0]


def test_annotate_and_save_writes_file(tmp_path):
    path = write_snapshot(tmp_path)
    count = annotate_and_save(path, "requests", "saved note")
    assert count == 1
    saved = json.loads(Path(path).read_text())
    assert saved["pip"][0]["note"] == "saved note"


def test_annotate_and_save_to_output(tmp_path):
    src = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    annotate_and_save(src, "lodash", "utility lib", output_path=out)
    saved = json.loads(Path(out).read_text())
    assert saved["npm"][0]["note"] == "utility lib"


def test_annotate_missing_file_raises(tmp_path):
    with pytest.raises(AnnotateError):
        annotate_and_save(str(tmp_path / "missing.json"), "x", "y")
