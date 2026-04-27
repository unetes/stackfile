"""Tests for stackfile.normalize."""

import json
import pytest
from pathlib import Path

from stackfile.normalize import (
    NormalizeError,
    _normalize_name,
    _normalize_version,
    _normalize_packages,
    normalize_snapshot,
)


def _base():
    return {
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [
            {"name": "My_Package", "version": "v1.2.3"},
            {"name": "another.lib", "version": "=0.9.0"},
        ],
        "npm": [
            {"name": "SomeLib", "version": "v2.0.0"},
        ],
        "brew": [],
    }


def write_snapshot(tmp_path, data=None):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data or _base()))
    return str(p)


def test_normalize_name_lowercases():
    assert _normalize_name("MyPackage") == "mypackage"


def test_normalize_name_replaces_underscores():
    assert _normalize_name("my_package") == "my-package"


def test_normalize_name_replaces_dots():
    assert _normalize_name("my.lib") == "my-lib"


def test_normalize_version_strips_leading_v():
    assert _normalize_version("v1.2.3") == "1.2.3"


def test_normalize_version_strips_equals():
    assert _normalize_version("=0.9.0") == "0.9.0"


def test_normalize_version_leaves_clean_version():
    assert _normalize_version("1.0.0") == "1.0.0"


def test_normalize_packages_returns_changed_count():
    packages = [
        {"name": "My_Lib", "version": "v1.0.0"},
        {"name": "clean", "version": "2.0.0"},
    ]
    result, changed = _normalize_packages(packages)
    assert changed == 1
    assert result[0]["name"] == "my-lib"
    assert result[0]["version"] == "1.0.0"
    assert result[1]["name"] == "clean"


def test_normalize_snapshot_writes_file(tmp_path):
    path = write_snapshot(tmp_path)
    result = normalize_snapshot(path)
    assert result["changed"] > 0
    data = json.loads(Path(path).read_text())
    assert data["pip"][0]["name"] == "my-package"
    assert data["pip"][0]["version"] == "1.2.3"


def test_normalize_snapshot_to_output_file(tmp_path):
    src = write_snapshot(tmp_path)
    out = str(tmp_path / "out.json")
    normalize_snapshot(src, output_path=out)
    assert Path(out).exists()
    data = json.loads(Path(out).read_text())
    assert data["pip"][1]["name"] == "another-lib"


def test_normalize_snapshot_section_flag(tmp_path):
    path = write_snapshot(tmp_path)
    normalize_snapshot(path, section="pip")
    data = json.loads(Path(path).read_text())
    # npm should remain unnormalized
    assert data["npm"][0]["name"] == "SomeLib"
    assert data["pip"][0]["version"] == "1.2.3"


def test_normalize_missing_file_raises():
    with pytest.raises(NormalizeError, match="File not found"):
        normalize_snapshot("/nonexistent/snap.json")


def test_normalize_returns_output_path(tmp_path):
    path = write_snapshot(tmp_path)
    result = normalize_snapshot(path)
    assert result["output"] == path
