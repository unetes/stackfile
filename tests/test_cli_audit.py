"""Integration tests for the audit CLI command."""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch

from stackfile.cli import main


@pytest.fixture
def snapshot_file(tmp_path):
    data = {
        "version": "1",
        "created_at": "2024-01-01",
        "dependencies": [
            {"manager": "pip", "packages": [{"name": "requests", "version": "2.28.0"}]},
            {"manager": "npm", "packages": [{"name": "lodash", "version": "4.0.0"}]},
        ],
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_audit_exits_zero_when_up_to_date(snapshot_file, capsys):
    with patch("stackfile.audit._run", return_value="{}"):
        rc = main(["audit", snapshot_file])
    assert rc == 0


def test_audit_exits_zero_with_json_flag(snapshot_file, capsys):
    with patch("stackfile.audit._run", return_value="{}"):
        rc = main(["audit", "--json", snapshot_file])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert isinstance(parsed, dict)


def test_audit_human_output_up_to_date(snapshot_file, capsys):
    with patch("stackfile.audit._run", return_value="{}"):
        main(["audit", snapshot_file])
    out = capsys.readouterr().out
    assert "up to date" in out


def test_audit_default_input(tmp_path, capsys):
    data = {"version": "1", "created_at": "2024-01-01", "dependencies": []}
    default = tmp_path / "stackfile.json"
    default.write_text(json.dumps(data))
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch("stackfile.audit._run", return_value="{}"):
            rc = main(["audit"])
        assert rc == 0
    finally:
        os.chdir(old)
