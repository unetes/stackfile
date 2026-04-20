"""Tests for stackfile.audit."""
from __future__ import annotations

import json
import os
import pytest
from unittest.mock import patch

from stackfile.audit import audit_snapshot, format_audit, _audit_npm, _audit_pip


@pytest.fixture
def snapshot_file(tmp_path):
    def _write(data):
        p = tmp_path / "snap.json"
        p.write_text(json.dumps(data))
        return str(p)
    return _write


def _make_snapshot(pip=None, npm=None):
    deps = []
    if pip is not None:
        deps.append({"manager": "pip", "packages": pip})
    if npm is not None:
        deps.append({"manager": "npm", "packages": npm})
    return {"version": "1", "created_at": "2024-01-01", "dependencies": deps}


def test_audit_empty_snapshot(snapshot_file):
    path = snapshot_file(_make_snapshot())
    results = audit_snapshot(path)
    assert results == {}


def test_audit_pip_empty_packages(snapshot_file):
    path = snapshot_file(_make_snapshot(pip=[]))
    results = audit_snapshot(path)
    assert results["pip"] == []


def test_audit_npm_empty_packages(snapshot_file):
    path = snapshot_file(_make_snapshot(npm=[]))
    results = audit_snapshot(path)
    assert results["npm"] == []


def test_audit_npm_outdated(snapshot_file):
    npm_data = json.dumps({"lodash": {"current": "4.0.0", "latest": "4.17.21"}})
    packages = [{"name": "lodash", "version": "4.0.0"}]
    path = snapshot_file(_make_snapshot(npm=packages))
    with patch("stackfile.audit._run", return_value=npm_data):
        results = audit_snapshot(path)
    assert len(results["npm"]) == 1
    assert results["npm"][0]["name"] == "lodash"
    assert results["npm"][0]["latest"] == "4.17.21"


def test_audit_npm_no_outdated(snapshot_file):
    packages = [{"name": "lodash", "version": "4.17.21"}]
    path = snapshot_file(_make_snapshot(npm=packages))
    with patch("stackfile.audit._run", return_value="{}"):
        results = audit_snapshot(path)
    assert results["npm"] == []


def test_format_audit_json():
    results = {"npm": [{"manager": "npm", "name": "lodash", "current": "4.0.0", "latest": "4.17.21"}]}
    out = format_audit(results, fmt="json")
    parsed = json.loads(out)
    assert parsed["npm"][0]["name"] == "lodash"


def test_format_audit_human_up_to_date():
    out = format_audit({"pip": [], "npm": []})
    assert "up to date" in out


def test_format_audit_human_shows_issues():
    results = {"npm": [{"manager": "npm", "name": "react", "current": "17.0.0", "latest": "18.0.0"}]}
    out = format_audit(results)
    assert "react" in out
    assert "17.0.0" in out
    assert "18.0.0" in out
