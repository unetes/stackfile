"""Tests for stackfile.doctor."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from stackfile.doctor import (
    CheckResult,
    DoctorError,
    DoctorReport,
    _check_tool,
    format_doctor,
    run_doctor,
    status_label,
)


@pytest.fixture
def snapshot_file(tmp_path):
    def _write(data: dict) -> str:
        p = tmp_path / "stack.json"
        p.write_text(json.dumps(data))
        return str(p)

    return _write


def _base_snapshot(**kwargs):
    data = {
        "version": "1",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [],
        "brew": [],
    }
    data.update(kwargs)
    return data


def test_status_label_ok():
    assert status_label(True) == "OK"


def test_status_label_missing():
    assert status_label(False) == "MISSING"


def test_doctor_report_all_ok_true():
    report = DoctorReport(results=[CheckResult("pip", True, "pip 23.0")])
    assert report.all_ok() is True


def test_doctor_report_all_ok_false():
    report = DoctorReport(
        results=[
            CheckResult("pip", True, "pip 23.0"),
            CheckResult("npm", False),
        ]
    )
    assert report.all_ok() is False


def test_doctor_report_to_dict():
    report = DoctorReport(results=[CheckResult("pip", True, "pip 23.0")])
    d = report.to_dict()
    assert d["all_ok"] is True
    assert d["checks"][0]["tool"] == "pip"


def test_run_doctor_missing_file(tmp_path):
    with pytest.raises(DoctorError, match="not found"):
        run_doctor(str(tmp_path / "missing.json"))


def test_run_doctor_returns_report(snapshot_file):
    path = snapshot_file(_base_snapshot())
    with patch("stackfile.doctor._check_tool") as mock_check:
        mock_check.return_value = CheckResult("pip", True, "pip 23.0")
        report = run_doctor(path)
    assert isinstance(report, DoctorReport)
    assert len(report.results) >= 1


def test_run_doctor_only_checks_used_tools(snapshot_file):
    path = snapshot_file(_base_snapshot(pip=[{"name": "flask", "version": "3.0"}], npm=[], brew=[]))
    checked = []
    with patch("stackfile.doctor._check_tool", side_effect=lambda t: checked.append(t) or CheckResult(t, True)):
        run_doctor(path)
    assert "pip" in checked
    assert "npm" not in checked


def test_format_doctor_contains_tool_name():
    report = DoctorReport(results=[CheckResult("pip", True, "pip 23.0")])
    output = format_doctor(report)
    assert "pip" in output
    assert "OK" in output


def test_format_doctor_shows_missing():
    report = DoctorReport(results=[CheckResult("npm", False)])
    output = format_doctor(report)
    assert "MISSING" in output
    assert "Some tools are missing" in output


def test_check_tool_unavailable():
    with patch("shutil.which", return_value=None):
        result = _check_tool("nonexistent_tool_xyz")
    assert result.available is False
    assert result.version is None
