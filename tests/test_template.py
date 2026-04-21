"""Tests for stackfile.template."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.template import (
    TemplateError,
    generate_template,
    save_template,
    PRESETS,
)


# ---------------------------------------------------------------------------
# generate_template
# ---------------------------------------------------------------------------

def test_blank_template_has_required_keys():
    snap = generate_template()
    for key in ("version", "created_at", "pip", "npm", "brew", "tags"):
        assert key in snap


def test_blank_template_has_empty_sections():
    snap = generate_template()
    assert snap["pip"] == []
    assert snap["npm"] == []
    assert snap["brew"] == []


def test_blank_template_description_default():
    snap = generate_template()
    assert snap["description"] == ""


def test_description_is_stored():
    snap = generate_template(description="my project")
    assert snap["description"] == "my project"


def test_python_preset_has_pip_packages():
    snap = generate_template(preset="python")
    names = [p["name"] for p in snap["pip"]]
    assert "requests" in names
    assert "click" in names


def test_python_preset_npm_is_empty():
    snap = generate_template(preset="python")
    assert snap["npm"] == []


def test_node_preset_has_npm_packages():
    snap = generate_template(preset="node")
    names = [p["name"] for p in snap["npm"]]
    assert "typescript" in names


def test_fullstack_preset_has_all_sections():
    snap = generate_template(preset="fullstack")
    assert len(snap["pip"]) > 0
    assert len(snap["npm"]) > 0
    assert len(snap["brew"]) > 0


def test_preset_case_insensitive():
    snap = generate_template(preset="Python")
    names = [p["name"] for p in snap["pip"]]
    assert "requests" in names


def test_unknown_preset_raises():
    with pytest.raises(TemplateError, match="Unknown preset"):
        generate_template(preset="cobol")


def test_all_defined_presets_are_valid():
    for name in PRESETS:
        snap = generate_template(preset=name)
        assert snap["version"] is not None


# ---------------------------------------------------------------------------
# save_template
# ---------------------------------------------------------------------------

def test_save_template_creates_file(tmp_path):
    out = str(tmp_path / "stack.json")
    save_template(out)
    assert Path(out).exists()


def test_save_template_valid_json(tmp_path):
    out = str(tmp_path / "stack.json")
    save_template(out, preset="node")
    data = json.loads(Path(out).read_text())
    assert "npm" in data


def test_save_template_returns_dict(tmp_path):
    out = str(tmp_path / "stack.json")
    result = save_template(out, preset="python")
    assert isinstance(result, dict)
    assert result["pip"][0]["name"] == "requests"
