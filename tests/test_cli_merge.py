import json
import pytest
from pathlib import Path
from unittest.mock import patch
from stackfile.cli import build_parser, main


@pytest.fixture
def two_snapshots(tmp_path):
    base = {
        "version": 1,
        "created_at": "2024-01-01T00:00:00+00:00",
        "packages": {"pip": [{"name": "flask", "version": "2.0.0"}]},
    }
    override = {
        "version": 1,
        "created_at": "2024-06-01T00:00:00+00:00",
        "packages": {"pip": [{"name": "flask", "version": "3.0.0"}]},
    }
    b = tmp_path / "base.json"
    o = tmp_path / "override.json"
    b.write_text(json.dumps(base))
    o.write_text(json.dumps(override))
    return str(b), str(o), tmp_path


def test_merge_exits_zero(two_snapshots):
    base, override, tmp_path = two_snapshots
    out = str(tmp_path / "merged.json")
    with patch("sys.argv", ["stackfile", "merge", base, override, "--output", out]):
        assert main() == 0


def test_merge_creates_output_file(two_snapshots):
    base, override, tmp_path = two_snapshots
    out = str(tmp_path / "merged.json")
    with patch("sys.argv", ["stackfile", "merge", base, override, "--output", out]):
        main()
    assert Path(out).exists()


def test_merge_output_contains_packages(two_snapshots):
    base, override, tmp_path = two_snapshots
    out = str(tmp_path / "merged.json")
    with patch("sys.argv", ["stackfile", "merge", base, override, "--output", out]):
        main()
    data = json.loads(Path(out).read_text())
    pip_versions = {p["name"]: p["version"] for p in data["packages"]["pip"]}
    assert pip_versions["flask"] == "3.0.0"
