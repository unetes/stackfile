"""Tests for stackfile.diff module."""

import json
import pytest
from pathlib import Path
from stackfile.diff import diff_snapshots, format_diff


@pytest.fixture
def write_snapshot(tmp_path):
    def _write(name, data):
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return str(p)
    return _write


BASE = {
    "pip": [{"name": "requests", "version": "2.28.0"}, {"name": "flask", "version": "2.0.0"}],
    "npm": [{"name": "lodash", "version": "4.17.21"}],
    "brew": [],
}

NEW = {
    "pip": [{"name": "requests", "version": "2.31.0"}, {"name": "click", "version": "8.1.0"}],
    "npm": [{"name": "lodash", "version": "4.17.21"}],
    "brew": [{"name": "git", "version": "2.40.0"}],
}


def test_diff_detects_added(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    assert "click==8.1.0" in diff["pip"]["added"]


def test_diff_detects_removed(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    assert "flask==2.0.0" in diff["pip"]["removed"]


def test_diff_detects_changed(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    assert any("requests" in c for c in diff["pip"]["changed"])


def test_diff_no_changes_in_npm(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    assert "npm" not in diff


def test_diff_brew_added(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    assert "git==2.40.0" in diff["brew"]["added"]


def test_format_diff_no_changes(write_snapshot):
    snap = write_snapshot("s.json", BASE)
    diff = diff_snapshots(snap, snap)
    assert format_diff(diff) == "No differences found."


def test_format_diff_contains_symbols(write_snapshot):
    old = write_snapshot("old.json", BASE)
    new = write_snapshot("new.json", NEW)
    diff = diff_snapshots(old, new)
    output = format_diff(diff)
    assert "+" in output
    assert "-" in output
    assert "~" in output
