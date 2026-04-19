import json
import pytest
from pathlib import Path
from stackfile.merge import merge_snapshots, merge_and_save


def write_snapshot(tmp_path, filename, data):
    p = tmp_path / filename
    p.write_text(json.dumps(data))
    return str(p)


BASE = {
    "version": 1,
    "created_at": "2024-01-01T00:00:00+00:00",
    "packages": {
        "pip": [{"name": "requests", "version": "2.28.0"}, {"name": "flask", "version": "2.0.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
    },
}

OVERRIDE = {
    "version": 1,
    "created_at": "2024-06-01T00:00:00+00:00",
    "packages": {
        "pip": [{"name": "requests", "version": "2.31.0"}, {"name": "numpy", "version": "1.26.0"}],
        "brew": [{"name": "git", "version": "2.44.0"}],
    },
}


def test_merge_override_wins_on_conflict(tmp_path):
    base = write_snapshot(tmp_path, "base.json", BASE)
    override = write_snapshot(tmp_path, "override.json", OVERRIDE)
    merged = merge_snapshots(base, override)
    pip_pkgs = {p["name"]: p["version"] for p in merged["packages"]["pip"]}
    assert pip_pkgs["requests"] == "2.31.0"


def test_merge_keeps_base_only_packages(tmp_path):
    base = write_snapshot(tmp_path, "base.json", BASE)
    override = write_snapshot(tmp_path, "override.json", OVERRIDE)
    merged = merge_snapshots(base, override)
    pip_pkgs = {p["name"] for p in merged["packages"]["pip"]}
    assert "flask" in pip_pkgs


def test_merge_adds_override_only_packages(tmp_path):
    base = write_snapshot(tmp_path, "base.json", BASE)
    override = write_snapshot(tmp_path, "override.json", OVERRIDE)
    merged = merge_snapshots(base, override)
    pip_pkgs = {p["name"] for p in merged["packages"]["pip"]}
    assert "numpy" in pip_pkgs


def test_merge_combines_sections(tmp_path):
    base = write_snapshot(tmp_path, "base.json", BASE)
    override = write_snapshot(tmp_path, "override.json", OVERRIDE)
    merged = merge_snapshots(base, override)
    assert "npm" in merged["packages"]
    assert "brew" in merged["packages"]


def test_merge_and_save_writes_file(tmp_path):
    base = write_snapshot(tmp_path, "base.json", BASE)
    override = write_snapshot(tmp_path, "override.json", OVERRIDE)
    out = str(tmp_path / "merged.json")
    merge_and_save(base, override, out)
    data = json.loads(Path(out).read_text())
    assert "packages" in data
    assert "created_at" in data
