"""Tests for stackfile/profile.py"""

import json
import pytest
from pathlib import Path
from stackfile.profile import (
    list_profiles,
    save_profile,
    load_profile,
    delete_profile,
    show_profile,
    ProfileError,
)


@pytest.fixture()
def profiles_dir(tmp_path):
    return tmp_path / "profiles"


@pytest.fixture()
def snapshot_file(tmp_path):
    snap = tmp_path / "stack.json"
    snap.write_text(json.dumps({"version": "1", "pip": [{"name": "requests", "version": "2.31.0"}]}))
    return snap


def test_list_profiles_empty_when_no_dir(profiles_dir):
    assert list_profiles(profiles_dir) == []


def test_save_profile_creates_file(snapshot_file, profiles_dir):
    dest = save_profile("dev", snapshot_file, profiles_dir)
    assert dest.exists()
    assert dest.name == "dev.json"


def test_list_profiles_returns_names(snapshot_file, profiles_dir):
    save_profile("alpha", snapshot_file, profiles_dir)
    save_profile("beta", snapshot_file, profiles_dir)
    assert list_profiles(profiles_dir) == ["alpha", "beta"]


def test_save_profile_invalid_name(snapshot_file, profiles_dir):
    with pytest.raises(ProfileError, match="Invalid profile name"):
        save_profile("my-profile!", snapshot_file, profiles_dir)


def test_save_profile_missing_snapshot(tmp_path, profiles_dir):
    with pytest.raises(ProfileError, match="Snapshot not found"):
        save_profile("dev", tmp_path / "missing.json", profiles_dir)


def test_save_profile_overwrites_existing(snapshot_file, tmp_path, profiles_dir):
    """Saving a profile with the same name should overwrite the existing file."""
    save_profile("dev", snapshot_file, profiles_dir)

    updated_snap = tmp_path / "updated.json"
    updated_snap.write_text(json.dumps({"version": "2", "pip": []}))
    save_profile("dev", updated_snap, profiles_dir)

    data = show_profile("dev", profiles_dir)
    assert data["version"] == "2"
    assert list_profiles(profiles_dir) == ["dev"]


def test_load_profile_copies_to_dest(snapshot_file, tmp_path, profiles_dir):
    save_profile("dev", snapshot_file, profiles_dir)
    out = tmp_path / "restored.json"
    load_profile("dev", out, profiles_dir)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["version"] == "1"


def test_load_profile_missing_raises(tmp_path, profiles_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        load_profile("ghost", tmp_path / "out.json", profiles_dir)


def test_delete_profile_removes_file(snapshot_file, profiles_dir):
    save_profile("dev", snapshot_file, profiles_dir)
    delete_profile("dev", profiles_dir)
    assert list_profiles(profiles_dir) == []


def test_delete_profile_missing_raises(profiles_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        delete_profile("nope", profiles_dir)


def test_show_profile_returns_dict(snapshot_file, profiles_dir):
    save_profile("prod", snapshot_file, profiles_dir)
    data = show_profile("prod", profiles_dir)
    assert "pip" in data


def test_show_profile_missing_raises(profiles_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        show_profile("missing", profiles_dir)
