"""Tests for stackfile.freeze."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stackfile.freeze import (
    FreezeError,
    _freeze_packages,
    _installed_pip,
    _installed_npm,
    freeze_snapshot,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


BASE = {
    "version": 1,
    "created_at": "2024-01-01T00:00:00",
    "pip": [{"name": "requests", "version": "*"}, {"name": "flask", "version": "3.0.0"}],
    "npm": [{"name": "typescript", "version": "latest"}],
    "brew": [{"name": "git", "version": ""}],
}


# ---------------------------------------------------------------------------
# Unit tests for _freeze_packages
# ---------------------------------------------------------------------------

def test_freeze_packages_replaces_wildcard():
    pkgs = [{"name": "requests", "version": "*"}]
    installed = {"requests": "2.31.0"}
    result = _freeze_packages(pkgs, installed)
    assert result[0]["version"] == "2.31.0"


def test_freeze_packages_replaces_latest():
    pkgs = [{"name": "typescript", "version": "latest"}]
    installed = {"typescript": "5.4.2"}
    result = _freeze_packages(pkgs, installed)
    assert result[0]["version"] == "5.4.2"


def test_freeze_packages_keeps_pinned_version():
    pkgs = [{"name": "flask", "version": "3.0.0"}]
    installed = {"flask": "3.1.0"}
    result = _freeze_packages(pkgs, installed)
    assert result[0]["version"] == "3.0.0"


def test_freeze_packages_unknown_package_keeps_original():
    pkgs = [{"name": "unknown-pkg", "version": "*"}]
    result = _freeze_packages(pkgs, {})
    assert result[0]["version"] == "*"


# ---------------------------------------------------------------------------
# Integration tests for freeze_snapshot
# ---------------------------------------------------------------------------

def test_freeze_snapshot_sets_frozen_flag(tmp_path):
    path = write_snapshot(tmp_path, BASE)
    pip_map = {"requests": "2.31.0", "flask": "3.0.0"}
    npm_map = {"typescript": "5.4.2"}
    with patch("stackfile.freeze._installed_pip", return_value=pip_map), \
         patch("stackfile.freeze._installed_npm", return_value=npm_map):
        result = freeze_snapshot(path)
    assert result["frozen"] is True


def test_freeze_snapshot_resolves_pip_versions(tmp_path):
    path = write_snapshot(tmp_path, BASE)
    pip_map = {"requests": "2.31.0", "flask": "3.0.0"}
    with patch("stackfile.freeze._installed_pip", return_value=pip_map), \
         patch("stackfile.freeze._installed_npm", return_value={}):
        result = freeze_snapshot(path)
    versions = {p["name"]: p["version"] for p in result["pip"]}
    assert versions["requests"] == "2.31.0"
    assert versions["flask"] == "3.0.0"


def test_freeze_snapshot_writes_to_custom_output(tmp_path):
    path = write_snapshot(tmp_path, BASE)
    out = str(tmp_path / "frozen.json")
    with patch("stackfile.freeze._installed_pip", return_value={}), \
         patch("stackfile.freeze._installed_npm", return_value={}):
        freeze_snapshot(path, output_path=out)
    data = json.loads(Path(out).read_text())
    assert data["frozen"] is True


def test_freeze_snapshot_raises_on_missing_file():
    with pytest.raises(FreezeError):
        freeze_snapshot("/nonexistent/path.json")
