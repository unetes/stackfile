"""Tests for stackfile.copy."""
import json
import pytest
from stackfile.copy import copy_packages, copy_and_save, CopyError


def _base():
    return {
        "version": "1",
        "pip": [{"name": "requests", "version": "2.28.0"}],
        "npm": [{"name": "lodash", "version": "4.17.21"}],
        "brew": [],
    }


def write_snapshot(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def test_copy_adds_new_packages():
    src = {"pip": [{"name": "flask", "version": "2.0.0"}], "npm": [], "brew": []}
    dst = _base()
    updated, count = copy_packages(src, dst)
    names = [p["name"] for p in updated["pip"]]
    assert "flask" in names
    assert count == 1


def test_copy_skips_existing_without_overwrite():
    src = {"pip": [{"name": "requests", "version": "99.0.0"}], "npm": [], "brew": []}
    dst = _base()
    updated, count = copy_packages(src, dst, overwrite=False)
    pkg = next(p for p in updated["pip"] if p["name"] == "requests")
    assert pkg["version"] == "2.28.0"
    assert count == 0


def test_copy_overwrites_existing_with_flag():
    src = {"pip": [{"name": "requests", "version": "99.0.0"}], "npm": [], "brew": []}
    dst = _base()
    updated, count = copy_packages(src, dst, overwrite=True)
    pkg = next(p for p in updated["pip"] if p["name"] == "requests")
    assert pkg["version"] == "99.0.0"
    assert count == 1


def test_copy_section_limits_scope():
    src = {
        "pip": [{"name": "flask", "version": "2.0.0"}],
        "npm": [{"name": "axios", "version": "1.0.0"}],
        "brew": [],
    }
    dst = _base()
    updated, count = copy_packages(src, dst, section="pip")
    pip_names = [p["name"] for p in updated["pip"]]
    npm_names = [p["name"] for p in updated["npm"]]
    assert "flask" in pip_names
    assert "axios" not in npm_names
    assert count == 1


def test_copy_and_save_writes_file(tmp_path):
    src_data = {"pip": [{"name": "black", "version": "22.0"}], "npm": [], "brew": []}
    dst_data = _base()
    src_path = write_snapshot(tmp_path, "src.json", src_data)
    dst_path = write_snapshot(tmp_path, "dst.json", dst_data)
    out_path = str(tmp_path / "out.json")
    count = copy_and_save(src_path, dst_path, output_path=out_path)
    result = json.loads((tmp_path / "out.json").read_text())
    names = [p["name"] for p in result["pip"]]
    assert "black" in names
    assert count == 1


def test_copy_raises_on_missing_src(tmp_path):
    dst_data = _base()
    dst_path = write_snapshot(tmp_path, "dst.json", dst_data)
    with pytest.raises(CopyError):
        copy_and_save(str(tmp_path / "nope.json"), dst_path)


def test_copy_raises_on_missing_dst(tmp_path):
    src_data = {"pip": [], "npm": [], "brew": []}
    src_path = write_snapshot(tmp_path, "src.json", src_data)
    with pytest.raises(CopyError):
        copy_and_save(src_path, str(tmp_path / "nope.json"))
