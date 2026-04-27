"""CLI integration tests for the classify command."""
import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0"},
            {"name": "pytest", "version": "7.4.0"},
        ],
        "npm": [
            {"name": "express", "version": "4.18.0"},
        ],
        "brew": [
            {"name": "git", "version": "2.43.0"},
        ],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_classify_exits_zero(snapshot_file):
    rc = main(["classify", "--input", snapshot_file])
    assert rc == 0


def test_classify_json_flag_prints_json(snapshot_file, capsys):
    main(["classify", "--input", snapshot_file, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "pip" in data


def test_classify_human_output_contains_category(snapshot_file, capsys):
    main(["classify", "--input", snapshot_file])
    captured = capsys.readouterr()
    assert "runtime" in captured.out or "dev" in captured.out


def test_classify_section_flag_limits_output(snapshot_file, capsys):
    main(["classify", "--input", snapshot_file, "--section", "pip"])
    captured = capsys.readouterr()
    assert "pip" in captured.out
    assert "npm" not in captured.out


def test_classify_nonzero_on_missing_file():
    rc = main(["classify", "--input", "/no/such/file.json"])
    assert rc != 0
