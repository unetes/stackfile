"""Integration tests for the CLI copy command."""
import json
import pytest
from stackfile.cli import main


def _base():
    return {
        "version": "1",
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [],
        "brew": [],
    }


@pytest.fixture()
def two_snapshots(tmp_path):
    src = tmp_path / "src.json"
    dst = tmp_path / "dst.json"
    src.write_text(json.dumps({"pip": [{"name": "flask", "version": "2.0.0"}], "npm": [], "brew": []}))
    dst.write_text(json.dumps(_base()))
    return str(src), str(dst)


def test_copy_exits_zero(two_snapshots, capsys):
    src, dst = two_snapshots
    rc = main(["copy", src, dst])
    assert rc == 0


def test_copy_prints_count(two_snapshots, capsys):
    src, dst = two_snapshots
    main(["copy", src, dst])
    out = capsys.readouterr().out
    assert "1 package" in out


def test_copy_creates_output_file(two_snapshots, tmp_path):
    src, dst = two_snapshots
    out = str(tmp_path / "result.json")
    main(["copy", src, dst, "-o", out])
    data = json.loads((tmp_path / "result.json").read_text())
    names = [p["name"] for p in data["pip"]]
    assert "flask" in names


def test_copy_section_flag(two_snapshots, tmp_path):
    src, dst = two_snapshots
    out = str(tmp_path / "result.json")
    rc = main(["copy", src, dst, "--section", "pip", "-o", out])
    assert rc == 0


def test_copy_nonzero_on_missing_src(tmp_path):
    dst = tmp_path / "dst.json"
    dst.write_text(json.dumps(_base()))
    rc = main(["copy", str(tmp_path / "nope.json"), str(dst)])
    assert rc != 0
