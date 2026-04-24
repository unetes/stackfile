"""Additional CLI tests for `stackfile filter` group and section flags."""

import json
import pytest
from pathlib import Path

from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [
            {"name": "requests", "version": "2.31.0", "group": "http"},
            {"name": "flask", "version": "3.0.0", "group": "web"},
            {"name": "pytest", "version": "7.4.0"},
        ],
        "npm": [
            {"name": "axios", "version": "1.6.0", "group": "http"},
            {"name": "express", "version": "4.18.0", "group": "web"},
        ],
        "brew": [{"name": "git", "version": "2.42.0"}],
    }
    p = tmp_path / "stackfile.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_filter_group_flag(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out, "--group", "http"])
    data = json.loads(Path(out).read_text())
    assert all(p.get("group") == "http" for p in data["pip"])
    assert all(p.get("group") == "http" for p in data["npm"])


def test_filter_section_flag_limits_scope(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out, "--section", "pip", "--name", "flask"])
    data = json.loads(Path(out).read_text())
    assert len(data["pip"]) == 1
    # npm should be untouched
    assert len(data["npm"]) == 2


def test_filter_version_flag(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out, "--version", "^2"])
    data = json.loads(Path(out).read_text())
    names = [p["name"] for p in data["pip"]]
    assert "requests" in names
    assert "flask" not in names


def test_filter_human_output_message(snapshot_file, tmp_path, capsys):
    out = str(tmp_path / "out.json")
    main(["filter", snapshot_file, "-o", out])
    captured = capsys.readouterr()
    assert "packages matched" in captured.out
