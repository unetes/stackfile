"""Tests for stackfile/alias.py"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from stackfile.alias import (
    AliasError,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    resolve_path_or_alias,
)


@pytest.fixture()
def alias_file(tmp_path: Path) -> Path:
    return tmp_path / "aliases.json"


def test_list_aliases_empty_when_missing(alias_file):
    assert list_aliases(alias_file) == {}


def test_add_alias_creates_entry(alias_file):
    add_alias("dev", "/home/user/dev.json", alias_file)
    aliases = list_aliases(alias_file)
    assert aliases["dev"] == "/home/user/dev.json"


def test_add_alias_invalid_name_raises(alias_file):
    with pytest.raises(AliasError, match="Invalid alias name"):
        add_alias("my-alias", "/some/path.json", alias_file)


def test_add_alias_overwrites_existing(alias_file):
    add_alias("prod", "/old/path.json", alias_file)
    add_alias("prod", "/new/path.json", alias_file)
    assert resolve_alias("prod", alias_file) == "/new/path.json"


def test_remove_alias_returns_true_when_found(alias_file):
    add_alias("staging", "/staging.json", alias_file)
    result = remove_alias("staging", alias_file)
    assert result is True
    assert resolve_alias("staging", alias_file) is None


def test_remove_alias_returns_false_when_missing(alias_file):
    result = remove_alias("nonexistent", alias_file)
    assert result is False


def test_resolve_alias_returns_none_for_unknown(alias_file):
    assert resolve_alias("unknown", alias_file) is None


def test_resolve_path_or_alias_returns_alias(alias_file):
    add_alias("local", "/local/stack.json", alias_file)
    assert resolve_path_or_alias("local", alias_file) == "/local/stack.json"


def test_resolve_path_or_alias_returns_value_when_not_alias(alias_file):
    assert resolve_path_or_alias("/direct/path.json", alias_file) == "/direct/path.json"


def test_list_aliases_returns_all_entries(alias_file):
    add_alias("a", "/a.json", alias_file)
    add_alias("b", "/b.json", alias_file)
    aliases = list_aliases(alias_file)
    assert len(aliases) == 2
    assert aliases["a"] == "/a.json"
    assert aliases["b"] == "/b.json"
