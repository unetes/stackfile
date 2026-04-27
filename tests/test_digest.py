"""Tests for stackfile.digest."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.digest import (
    DigestError,
    compute_digest,
    digest_snapshot,
    format_digest,
    verify_digest,
)


@pytest.fixture()
def snapshot_file(tmp_path: Path) -> Path:
    data = {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00",
        "pip": [{"name": "requests", "version": "2.31.0"}],
        "npm": [],
        "brew": [],
    }
    p = tmp_path / "snapshot.json"
    p.write_text(json.dumps(data))
    return p


def test_compute_digest_returns_string(snapshot_file):
    data = json.loads(snapshot_file.read_text())
    result = compute_digest(data)
    assert isinstance(result, str)
    assert len(result) == 64  # sha256 hex length


def test_compute_digest_is_deterministic(snapshot_file):
    data = json.loads(snapshot_file.read_text())
    assert compute_digest(data) == compute_digest(data)


def test_compute_digest_changes_with_data(snapshot_file):
    data = json.loads(snapshot_file.read_text())
    modified = dict(data)
    modified["pip"] = [{"name": "flask", "version": "3.0.0"}]
    assert compute_digest(data) != compute_digest(modified)


def test_compute_digest_md5_length(snapshot_file):
    data = json.loads(snapshot_file.read_text())
    result = compute_digest(data, algorithm="md5")
    assert len(result) == 32


def test_compute_digest_unsupported_algorithm(snapshot_file):
    data = json.loads(snapshot_file.read_text())
    with pytest.raises(DigestError, match="Unsupported"):
        compute_digest(data, algorithm="notreal")


def test_digest_snapshot_returns_dict(snapshot_file):
    result = digest_snapshot(str(snapshot_file))
    assert "digest" in result
    assert result["algorithm"] == "sha256"
    assert result["path"] == str(snapshot_file)


def test_digest_snapshot_missing_file(tmp_path):
    with pytest.raises(DigestError, match="File not found"):
        digest_snapshot(str(tmp_path / "missing.json"))


def test_verify_digest_true(snapshot_file):
    result = digest_snapshot(str(snapshot_file))
    assert verify_digest(str(snapshot_file), result["digest"]) is True


def test_verify_digest_false(snapshot_file):
    assert verify_digest(str(snapshot_file), "deadbeef") is False


def test_format_digest_human(snapshot_file):
    result = digest_snapshot(str(snapshot_file))
    output = format_digest(result)
    assert "sha256:" in output
    assert str(snapshot_file) in output


def test_format_digest_json(snapshot_file):
    result = digest_snapshot(str(snapshot_file))
    output = format_digest(result, fmt="json")
    parsed = json.loads(output)
    assert parsed["algorithm"] == "sha256"
    assert "digest" in parsed
