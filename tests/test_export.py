"""Tests for stackfile.export module."""
import json
import pytest
from pathlib import Path
from stackfile.export import export_shell, export_requirements_txt, export_snapshot


SAMPLE = {
    "pip": {"requests": "2.31.0", "flask": "3.0.0"},
    "npm": {"typescript": "5.4.5"},
    "brew": {"git": "2.44.0"},
}


def write_snapshot(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "stack.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_export_shell_contains_pip(tmp_path):
    script = export_shell(SAMPLE)
    assert "pip install 'requests==2.31.0'" in script
    assert "pip install 'flask==3.0.0'" in script


def test_export_shell_contains_npm(tmp_path):
    script = export_shell(SAMPLE)
    assert "npm install -g 'typescript@5.4.5'" in script


def test_export_shell_contains_brew(tmp_path):
    script = export_shell(SAMPLE)
    assert "brew install 'git'" in script


def test_export_shell_shebang():
    script = export_shell(SAMPLE)
    assert script.startswith("#!/usr/bin/env bash")


def test_export_requirements_txt():
    txt = export_requirements_txt(SAMPLE)
    assert "requests==2.31.0" in txt
    assert "flask==3.0.0" in txt
    assert "typescript" not in txt


def test_export_requirements_empty():
    txt = export_requirements_txt({"pip": {}})
    assert txt == ""


def test_export_snapshot_shell(tmp_path):
    src = write_snapshot(tmp_path, SAMPLE)
    out = str(tmp_path / "install.sh")
    export_snapshot(src, out, "shell")
    content = Path(out).read_text()
    assert "pip install" in content


def test_export_snapshot_requirements(tmp_path):
    src = write_snapshot(tmp_path, SAMPLE)
    out = str(tmp_path / "requirements.txt")
    export_snapshot(src, out, "requirements")
    content = Path(out).read_text()
    assert "requests==2.31.0" in content


def test_export_snapshot_unknown_format(tmp_path):
    src = write_snapshot(tmp_path, SAMPLE)
    with pytest.raises(ValueError, match="Unknown export format"):
        export_snapshot(src, str(tmp_path / "out"), "yaml")
