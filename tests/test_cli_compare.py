"""CLI integration tests for the 'compare' subcommand."""

import json
from pathlib import Path

import pytest

from stackfile.cli import main


def _write(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def _snap(pip=None) -> dict:
    pkgs = ["name": n, "version": v} for n, v in (pip or {}).items()]
    return {"version": "1", "pip": {"packages": pkgs}, "npm": {"packages": []}, "brew": {"packages": []}}


@pytest.fixture()
def two_snapshots(tmp_path):
    a = _write(tmp_path, "a.json", _snap(pip={"requests": "2.31.0"}))
    b = _write(tmp_path, "b.json", _snap(pip={"requests": "2.28.0", "flask": "3.0.0"}))
    return a, b


def test_compare_exits_zero(two_snapshots, capsys):
    a, b = two_snapshots
    rc = main(["compare", a, b])
    assert rc == 0


def test_compare_json_flag(two_snapshots, capsys):
    a, b = two_snapshots
    main(["compare", a, b, "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "overall_similarity_pct" in data
    assert "sections" in data


def test_compare_human_output(two_snapshots, capsys):
    a, b = two_snapshots
    main(["compare", a, b])
    out = capsys.readouterr().out
    assert "[pip]" in out
    assert "Overall similarity" in out


def test_compare_identical_snapshots(tmp_path, capsys):
    snap = _snap(pip={"requests": "2.31.0"})
    a = _write(tmp_path, "a.json", snap)
    b = _write(tmp_path, "b.json", snap)
    main(["compare", a, b])
    out = capsys.readouterr().out
    assert "100.0%" in out


def test_compare_missing_file_exits_nonzero(tmp_path):
    """Passing a non-existent file path should cause a non-zero exit code."""
    real = _write(tmp_path, "a.json", _snap(pip={"requests": "2.31.0"}))
    missing = str(tmp_path / "does_not_exist.json")
    rc = main(["compare", real, missing])
    assert rc != 0
