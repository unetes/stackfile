"""CLI integration tests for the digest command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackfile.cli import main


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


def test_digest_exits_zero(snapshot_file, capsys):
    rc = main(["digest", str(snapshot_file)])
    assert rc == 0


def test_digest_human_output_contains_sha256(snapshot_file, capsys):
    main(["digest", str(snapshot_file)])
    out = capsys.readouterr().out
    assert "sha256:" in out


def test_digest_json_flag_prints_json(snapshot_file, capsys):
    main(["digest", str(snapshot_file), "--json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "digest" in parsed
    assert parsed["algorithm"] == "sha256"


def test_digest_algorithm_flag(snapshot_file, capsys):
    main(["digest", str(snapshot_file), "--algorithm", "md5"])
    out = capsys.readouterr().out
    assert "md5:" in out


def test_digest_missing_file_exits_nonzero(tmp_path, capsys):
    rc = main(["digest", str(tmp_path / "missing.json")])
    assert rc != 0


def test_digest_verify_flag_exits_zero(snapshot_file, capsys):
    from stackfile.digest import digest_snapshot
    expected = digest_snapshot(str(snapshot_file))["digest"]
    rc = main(["digest", str(snapshot_file), "--verify", expected])
    assert rc == 0


def test_digest_verify_flag_exits_nonzero_on_mismatch(snapshot_file, capsys):
    rc = main(["digest", str(snapshot_file), "--verify", "deadbeef"])
    assert rc != 0
