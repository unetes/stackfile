"""CLI integration tests for the 'score' subcommand."""
import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> str:
    data = {
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "requests", "version": "2.31.0", "pinned": True},
            {"name": "flask", "version": "*"},
        ],
        "npm": [{"name": "lodash", "version": "4.17.21", "pinned": True, "note": "utility"}],
        "brew": [],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_score_exits_zero(snapshot_file, capsys):
    rc = main(["score", snapshot_file])
    assert rc == 0


def test_score_human_output_contains_overall(snapshot_file, capsys):
    main(["score", snapshot_file])
    out = capsys.readouterr().out
    assert "Overall score" in out


def test_score_human_output_contains_grade(snapshot_file, capsys):
    main(["score", snapshot_file])
    out = capsys.readouterr().out
    assert "Grade" in out


def test_score_json_flag_prints_json(snapshot_file, capsys):
    main(["score", "--json", snapshot_file])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "overall" in parsed
    assert "sections" in parsed
    assert "grade" in parsed


def test_score_json_sections_have_metrics(snapshot_file, capsys):
    main(["score", "--json", snapshot_file])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    pip_metrics = parsed["sections"]["pip"]
    assert "total" in pip_metrics
    assert "pinned" in pip_metrics
    assert "versioned" in pip_metrics


def test_score_default_input_is_stackfile_json(tmp_path, monkeypatch, capsys):
    data = {"version": "1", "created_at": "2024-01-01", "pip": [], "npm": [], "brew": []}
    (tmp_path / "stackfile.json").write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    rc = main(["score"])
    assert rc == 0
