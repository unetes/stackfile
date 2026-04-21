"""CLI integration tests for the profile sub-command."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    snap = tmp_path / "stack.json"
    snap.write_text(json.dumps({"version": "1", "pip": [{"name": "flask", "version": "3.0.0"}]}))
    return snap


@pytest.fixture()
def profiles_dir(tmp_path):
    return tmp_path / "profiles"


def test_profile_save_exits_zero(snapshot_file, profiles_dir, capsys):
    rc = main(["profile", "save", "dev",
               "--input", str(snapshot_file),
               "--profiles-dir", str(profiles_dir)])
    assert rc == 0


def test_profile_list_exits_zero(snapshot_file, profiles_dir, capsys):
    main(["profile", "save", "dev",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    rc = main(["profile", "list", "--profiles-dir", str(profiles_dir)])
    assert rc == 0


def test_profile_list_shows_name(snapshot_file, profiles_dir, capsys):
    main(["profile", "save", "staging",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    main(["profile", "list", "--profiles-dir", str(profiles_dir)])
    out = capsys.readouterr().out
    assert "staging" in out


def test_profile_load_exits_zero(snapshot_file, tmp_path, profiles_dir, capsys):
    main(["profile", "save", "dev",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    out_file = tmp_path / "restored.json"
    rc = main(["profile", "load", "dev",
               "--output", str(out_file),
               "--profiles-dir", str(profiles_dir)])
    assert rc == 0
    assert out_file.exists()


def test_profile_delete_exits_zero(snapshot_file, profiles_dir):
    main(["profile", "save", "dev",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    rc = main(["profile", "delete", "dev", "--profiles-dir", str(profiles_dir)])
    assert rc == 0


def test_profile_save_invalid_name_exits_nonzero(snapshot_file, profiles_dir):
    rc = main(["profile", "save", "bad-name!",
               "--input", str(snapshot_file),
               "--profiles-dir", str(profiles_dir)])
    assert rc != 0
