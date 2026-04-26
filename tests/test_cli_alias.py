"""CLI integration tests for the alias subcommand."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stackfile.cli import main


@pytest.fixture()
def alias_file(tmp_path: Path) -> Path:
    return tmp_path / "aliases.json"


def _run(args, alias_file):
    with patch("stackfile.alias.ALIAS_FILE", alias_file):
        return main(args)


def test_alias_add_exits_zero(alias_file):
    rc = _run(["alias", "add", "dev", "/dev/stack.json"], alias_file)
    assert rc == 0


def test_alias_add_persists(alias_file):
    _run(["alias", "add", "dev", "/dev/stack.json"], alias_file)
    assert alias_file.exists()
    data = json.loads(alias_file.read_text())
    assert data["dev"] == "/dev/stack.json"


def test_alias_remove_exits_zero(alias_file):
    _run(["alias", "add", "dev", "/dev/stack.json"], alias_file)
    rc = _run(["alias", "remove", "dev"], alias_file)
    assert rc == 0


def test_alias_remove_nonexistent_exits_nonzero(alias_file):
    rc = _run(["alias", "remove", "ghost"], alias_file)
    assert rc != 0


def test_alias_list_exits_zero(alias_file):
    rc = _run(["alias", "list"], alias_file)
    assert rc == 0


def test_alias_list_shows_entries(alias_file, capsys):
    _run(["alias", "add", "prod", "/prod.json"], alias_file)
    _run(["alias", "list"], alias_file)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "/prod.json" in out
