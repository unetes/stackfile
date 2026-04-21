"""Tests for stackfile/lint.py"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from stackfile.lint import lint_snapshot, format_lint_results, lint_and_print, LintError


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snapshot.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base() -> dict:
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "tags": ["dev"],
        "pip": [],
        "npm": [],
        "brew": [],
    }


def test_no_warnings_for_clean_snapshot():
    data = _base()
    data["pip"] = [{"name": "requests", "version": "2.31.0", "pinned": True}]
    assert lint_snapshot(data) == []


def test_warns_on_unpinned_version():
    data = _base()
    data["pip"] = [{"name": "flask", "version": "latest"}]
    warnings = lint_snapshot(data)
    assert any("flask" in w and "pinned" in w for w in warnings)


def test_warns_on_missing_version():
    data = _base()
    data["npm"] = [{"name": "lodash", "version": ""}]
    warnings = lint_snapshot(data)
    assert any("lodash" in w for w in warnings)


def test_warns_on_explicitly_unpinned_flag():
    data = _base()
    data["brew"] = [{"name": "git", "version": "2.40.0", "pinned": False}]
    warnings = lint_snapshot(data)
    assert any("git" in w and "unpinned" in w for w in warnings)


def test_warns_on_missing_tags():
    data = _base()
    data["tags"] = []
    warnings = lint_snapshot(data)
    assert any("tags" in w for w in warnings)


def test_warns_on_missing_created_at():
    data = _base()
    data["created_at"] = ""
    warnings = lint_snapshot(data)
    assert any("created_at" in w for w in warnings)


def test_format_no_warnings():
    assert format_lint_results([]) == "No lint warnings found."


def test_format_with_warnings():
    result = format_lint_results(["[pip] 'x' has no pinned version"])
    assert "Lint warnings:" in result
    assert "[pip]" in result


def test_lint_and_print_exits_zero(tmp_path, capsys):
    path = write_snapshot(tmp_path, _base())
    code = lint_and_print(path)
    assert code == 0
    out = capsys.readouterr().out
    assert "No lint warnings" in out


def test_lint_and_print_json_flag(tmp_path, capsys):
    data = _base()
    data["tags"] = []
    path = write_snapshot(tmp_path, data)
    code = lint_and_print(path, as_json=True)
    assert code == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "warnings" in parsed
    assert parsed["count"] >= 1


def test_lint_and_print_bad_file(tmp_path, capsys):
    code = lint_and_print(str(tmp_path / "missing.json"))
    assert code == 1
