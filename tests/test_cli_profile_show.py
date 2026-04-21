"""Extra CLI tests: profile show and edge cases."""

import json
import pytest
from pathlib import Path
from stackfile.cli import main


@pytest.fixture()
def snapshot_file(tmp_path):
    snap = tmp_path / "stack.json"
    snap.write_text(json.dumps({
        "version": "1",
        "created_at": "2024-01-01",
        "pip": [{"name": "django", "version": "5.0.0"}],
        "npm": [],
        "brew": [],
    }))
    return snap


@pytest.fixture()
def profiles_dir(tmp_path):
    return tmp_path / "profs"


def test_profile_show_exits_zero(snapshot_file, profiles_dir, capsys):
    main(["profile", "save", "prod",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    rc = main(["profile", "show", "prod", "--profiles-dir", str(profiles_dir)])
    assert rc == 0


def test_profile_show_prints_json(snapshot_file, profiles_dir, capsys):
    main(["profile", "save", "prod",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    main(["profile", "show", "prod", "--profiles-dir", str(profiles_dir)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "pip" in data


def test_profile_list_empty_message(profiles_dir, capsys):
    main(["profile", "list", "--profiles-dir", str(profiles_dir)])
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_profile_load_missing_exits_nonzero(tmp_path, profiles_dir):
    rc = main(["profile", "load", "ghost",
               "--output", str(tmp_path / "out.json"),
               "--profiles-dir", str(profiles_dir)])
    assert rc != 0


def test_profile_delete_missing_exits_nonzero(profiles_dir):
    rc = main(["profile", "delete", "ghost", "--profiles-dir", str(profiles_dir)])
    assert rc != 0


def test_profile_save_then_list_then_delete(snapshot_file, profiles_dir, capsys):
    main(["profile", "save", "ci",
          "--input", str(snapshot_file),
          "--profiles-dir", str(profiles_dir)])
    main(["profile", "list", "--profiles-dir", str(profiles_dir)])
    assert "ci" in capsys.readouterr().out
    main(["profile", "delete", "ci", "--profiles-dir", str(profiles_dir)])
    main(["profile", "list", "--profiles-dir", str(profiles_dir)])
    assert "ci" not in capsys.readouterr().out
