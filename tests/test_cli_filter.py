"""Integration tests for the `stackfile filter` CLI sub-command."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0", "group": "http"},
            {"name": "flask", "version": "3.0.0"},
        ],
        "npm": [{"name": "axios", "version": "1.6.0"}],
        "brew": [{"name": "git", "version": "2.42.0"}],
    }
    p = tmp_path / "stackfile.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_filter_exits_zero(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    rc = main(["filter", snapshot_file, "-o", out])
    assert rc == 0


def test_filter_creates_output_file(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out])
    assert Path(out).exists()


def test_filter_by_name_reduces_packages(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out, "--name", "flask"])
    data = json.loads(Path(out).read_text())
    assert len(data["pip"]) == 1
    assert data["pip"][0]["name"] == "flask"


def test_filter_json_flag_prints_json(snapshot_file, tmp_path, capsys):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out, "--json"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert "pip" in parsed


def test_filter_missing_file_returns_nonzero(tmp_path):
    rc = main(["filter", str(tmp_path / "nope.json")])
    assert rc != 0
