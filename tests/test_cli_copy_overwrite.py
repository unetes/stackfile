"""Tests for the --overwrite flag of the CLI copy command."""
import json
import pytest
from stackfile.cli import main


@pytest.fixture()
def overlapping_snapshots(tmp_path):
    src = tmp_path / "src.json"
    dst = tmp_path / "dst.json"
    src.write_text(json.dumps({
        "pip": [{"name": "requests", "version": "99.9.9"}],
        "npm": [],
        "brew": [],
    }))
    dst.write_text(json.dumps({
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [],
        "brew": [],
    }))
    return str(src), str(dst)


def test_overwrite_flag_updates_version(overlapping_snapshots, tmp_path):
    src, dst = overlapping_snapshots
    out = str(tmp_path / "out.json")
    main(["copy", src, dst, "--overwrite", "-o", out])
    data = json.loads((tmp_path / "out.json").read_text())
    pkg = next(p for p in data["pip"] if p["name"] == "requests")
    assert pkg["version"] == "99.9.9"


def test_no_overwrite_keeps_original_version(overlapping_snapshots, tmp_path):
    src, dst = overlapping_snapshots
    out = str(tmp_path / "out.json")
    main(["copy", src, dst, "-o", out])
    data = json.loads((tmp_path / "out.json").read_text())
    pkg = next(p for p in data["pip"] if p["name"] == "requests")
    assert pkg["version"] == "2.28.0"


def test_overwrite_exits_zero(overlapping_snapshots):
    src, dst = overlapping_snapshots
    rc = main(["copy", src, dst, "--overwrite"])
    assert rc == 0


def test_copy_count_zero_when_no_new_packages(overlapping_snapshots, capsys):
    src, dst = overlapping_snapshots
    main(["copy", src, dst])
    out = capsys.readouterr().out
    assert "0 package" in out
