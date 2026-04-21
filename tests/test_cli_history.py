"""CLI integration tests for the history command."""

import json
import pytest
from unittest.mock import patch, MagicMock
from stackfile.cli import main


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.jsonl")


def test_history_list_exits_zero(history_file):
    with patch("stackfile.history.DEFAULT_HISTORY_FILE", history_file):
        ret = main(["history", "list", "--history-file", history_file])
    assert ret == 0


def test_history_list_empty_message(history_file, capsys):
    ret = main(["history", "list", "--history-file", history_file])
    out = capsys.readouterr().out
    assert "No history" in out
    assert ret == 0


def test_history_list_shows_entries(history_file, capsys):
    from stackfile.history import record_event
    record_event("snapshot", "stack.json", history_file)
    ret = main(["history", "list", "--history-file", history_file])
    out = capsys.readouterr().out
    assert "snapshot" in out
    assert ret == 0


def test_history_clear_exits_zero(history_file):
    ret = main(["history", "clear", "--history-file", history_file])
    assert ret == 0


def test_history_list_json_flag(history_file, capsys):
    from stackfile.history import record_event
    record_event("restore", "stack.json", history_file)
    ret = main(["history", "list", "--json", "--history-file", history_file])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["event"] == "restore"
    assert ret == 0
