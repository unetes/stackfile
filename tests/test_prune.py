"""Tests for stackfile.prune."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from stackfile.prune import PruneError, prune_snapshot


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


def _base(pip=None, npm=None, brew=None):
    return {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": {"packages": pip or []},
        "npm": {"packages": npm or []},
        "brew": {"packages": brew or []},
    }


@pytest.fixture()
def snapshot_file(tmp_path):
    data = _base(
        pip=[{"name": "requests"}, {"name": "flask"}, {"name": "ghost-pkg"}],
        npm=[{"name": "lodash"}, {"name": "phantom"}],
        brew=[{"name": "git"}, {"name": "wget"}],
    )
    return write_snapshot(tmp_path, data)


def test_prune_removes_uninstalled_pip(snapshot_file, tmp_path):
    out = tmp_path / "pruned.json"
    with patch("stackfile.prune._installed_pip", return_value={"requests", "flask"}), \
         patch("stackfile.prune._installed_npm", return_value={"lodash", "phantom"}), \
         patch("stackfile.prune._installed_brew", return_value={"git", "wget"}):
        result = prune_snapshot(snapshot_file, str(out))

    pip_names = [p["name"] for p in result["snapshot"]["pip"]["packages"]]
    assert "ghost-pkg" not in pip_names
    assert "requests" in pip_names
    assert result["pruned"].get("pip") == 1


def test_prune_removes_uninstalled_npm(snapshot_file, tmp_path):
    out = tmp_path / "pruned.json"
    with patch("stackfile.prune._installed_pip", return_value={"requests", "flask", "ghost-pkg"}), \
         patch("stackfile.prune._installed_npm", return_value={"lodash"}), \
         patch("stackfile.prune._installed_brew", return_value={"git", "wget"}):
        result = prune_snapshot(snapshot_file, str(out))

    npm_names = [p["name"] for p in result["snapshot"]["npm"]["packages"]]
    assert "phantom" not in npm_names
    assert "lodash" in npm_names
    assert result["pruned"].get("npm") == 1


def test_prune_writes_output_file(snapshot_file, tmp_path):
    out = tmp_path / "out.json"
    with patch("stackfile.prune._installed_pip", return_value=set()), \
         patch("stackfile.prune._installed_npm", return_value=set()), \
         patch("stackfile.prune._installed_brew", return_value=set()):
        prune_snapshot(snapshot_file, str(out))

    assert out.exists()
    data = json.loads(out.read_text())
    assert data["pip"]["packages"] == []


def test_prune_overwrites_input_when_no_output(snapshot_file):
    with patch("stackfile.prune._installed_pip", return_value={"requests"}), \
         patch("stackfile.prune._installed_npm", return_value=set()), \
         patch("stackfile.prune._installed_brew", return_value=set()):
        prune_snapshot(snapshot_file)

    data = json.loads(Path(snapshot_file).read_text())
    pip_names = [p["name"] for p in data["pip"]["packages"]]
    assert pip_names == ["requests"]


def test_prune_no_changes_when_all_installed(snapshot_file, tmp_path):
    out = tmp_path / "out.json"
    with patch("stackfile.prune._installed_pip", return_value={"requests", "flask", "ghost-pkg"}), \
         patch("stackfile.prune._installed_npm", return_value={"lodash", "phantom"}), \
         patch("stackfile.prune._installed_brew", return_value={"git", "wget"}):
        result = prune_snapshot(snapshot_file, str(out))

    assert result["pruned"] == {}


def test_prune_raises_on_missing_file(tmp_path):
    with pytest.raises(PruneError):
        prune_snapshot(str(tmp_path / "nonexistent.json"))
