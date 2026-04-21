"""Tests for stackfile/history.py"""

import json
import os
import pytest
from stackfile.history import (
    record_event,
    list_history,
    clear_history,
    format_history,
    HistoryError,
)


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.jsonl")


def test_list_history_empty_when_missing(history_file):
    entries = list_history(history_file)
    assert entries == []


def test_record_event_creates_file(history_file):
    record_event("snapshot", "stack.json", history_file)
    assert os.path.exists(history_file)


def test_record_event_appends_entry(history_file):
    record_event("snapshot", "stack.json", history_file)
    record_event("restore", "stack.json", history_file)
    entries = list_history(history_file)
    assert len(entries) == 2
    assert entries[0]["event"] == "snapshot"
    assert entries[1]["event"] == "restore"


def test_record_event_stores_snapshot_path(history_file):
    record_event("snapshot", "/path/to/stack.json", history_file)
    entries = list_history(history_file)
    assert entries[0]["snapshot"] == "/path/to/stack.json"


def test_record_event_stores_timestamp(history_file):
    record_event("snapshot", "stack.json", history_file)
    entries = list_history(history_file)
    assert "timestamp" in entries[0]
    assert entries[0]["timestamp"].endswith("Z")


def test_clear_history_removes_file(history_file):
    record_event("snapshot", "stack.json", history_file)
    clear_history(history_file)
    assert not os.path.exists(history_file)


def test_clear_history_no_error_when_missing(history_file):
    clear_history(history_file)  # should not raise


def test_format_history_empty():
    result = format_history([])
    assert result == "No history recorded."


def test_format_history_contains_event_and_path(history_file):
    record_event("snapshot", "stack.json", history_file)
    entries = list_history(history_file)
    result = format_history(entries)
    assert "snapshot" in result
    assert "stack.json" in result


def test_corrupt_history_raises(history_file):
    with open(history_file, "w") as f:
        f.write("not-valid-json\n")
    with pytest.raises(HistoryError):
        list_history(history_file)
