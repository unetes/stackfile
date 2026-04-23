"""Tests for stackfile.notes."""

import json
import pytest
from pathlib import Path
from stackfile.notes import list_notes, format_notes, notes_and_print, NotesError


def _snap(tmp_path, data):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0", "note": "HTTP lib"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [{"name": "lodash", "version": "4.17.21", "note": "utility"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    }


def test_list_notes_finds_annotated(tmp_path):
    entries = list_notes(_base())
    names = [e[1] for e in entries]
    assert "requests" in names
    assert "lodash" in names


def test_list_notes_excludes_unannotated():
    entries = list_notes(_base())
    names = [e[1] for e in entries]
    assert "flask" not in names
    assert "git" not in names


def test_list_notes_returns_section():
    entries = list_notes(_base())
    sections = {e[1]: e[0] for e in entries}
    assert sections["requests"] == "pip"
    assert sections["lodash"] == "npm"


def test_list_notes_empty_snapshot():
    data = {"pip": [], "npm": [], "brew": []}
    assert list_notes(data) == []


def test_format_notes_no_entries():
    assert format_notes([]) == "No annotations found."


def test_format_notes_includes_section_and_name():
    entries = [("pip", "requests", "HTTP lib")]
    out = format_notes(entries)
    assert "[pip]" in out
    assert "requests" in out
    assert "HTTP lib" in out


def test_notes_and_print_exits_zero(tmp_path, capsys):
    path = _snap(tmp_path, _base())
    rc = notes_and_print(path)
    assert rc == 0


def test_notes_and_print_json_flag(tmp_path, capsys):
    path = _snap(tmp_path, _base())
    notes_and_print(path, as_json=True)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert any(e["name"] == "requests" for e in parsed)


def test_notes_missing_file_raises(tmp_path):
    with pytest.raises(NotesError):
        notes_and_print(str(tmp_path / "missing.json"))
