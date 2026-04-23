"""watch.py — Monitor a snapshot file for changes and report drift from installed packages."""

import json
import time
import subprocess
from pathlib import Path
from typing import Optional


class WatchError(Exception):
    """Raised when the watch command encounters an unrecoverable error."""


def _load(path: str) -> dict:
    """Load and return a snapshot dict from *path*."""
    with open(path) as fh:
        return json.load(fh)


def _run(cmd: list[str]) -> str:
    """Run *cmd* and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception:
        return ""


def _installed_pip() -> dict[str, str]:
    """Return a mapping of package name -> installed version for pip."""
    raw = _run(["pip", "list", "--format=json"])
    try:
        entries = json.loads(raw)
        return {e["name"].lower(): e["version"] for e in entries}
    except Exception:
        return {}


def _installed_npm() -> dict[str, str]:
    """Return a mapping of package name -> installed version for npm (global)."""
    raw = _run(["npm", "list", "-g", "--json", "--depth=0"])
    try:
        data = json.loads(raw)
        deps = data.get("dependencies", {})
        return {name: info.get("version", "unknown") for name, info in deps.items()}
    except Exception:
        return {}


def _installed_brew() -> dict[str, str]:
    """Return a mapping of formula name -> installed version for Homebrew."""
    raw = _run(["brew", "list", "--versions"])
    result: dict[str, str] = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            result[parts[0]] = parts[-1]
    return result


def _detect_drift(
    snapshot: dict,
    pip: dict[str, str],
    npm: dict[str, str],
    brew: dict[str, str],
) -> list[dict]:
    """Compare snapshot packages against installed versions and return drift entries."""
    drift: list[dict] = []

    section_map = {
        "pip": pip,
        "npm": npm,
        "brew": brew,
    }

    for section, installed in section_map.items():
        for pkg in snapshot.get(section, {}).get("packages", []):
            name = pkg.get("name", "").lower()
            pinned = pkg.get("version", "")
            if not name:
                continue
            actual = installed.get(name)
            if actual is None:
                drift.append({"section": section, "package": name, "pinned": pinned, "installed": None, "status": "missing"})
            elif pinned and pinned not in ("*", "latest", "") and actual != pinned:
                drift.append({"section": section, "package": name, "pinned": pinned, "installed": actual, "status": "version_mismatch"})

    return drift


def watch_snapshot(
    path: str,
    interval: int = 30,
    on_drift=None,
    stop_after: Optional[int] = None,
) -> None:
    """Poll *path* every *interval* seconds and call *on_drift* with drift results.

    Args:
        path: Path to the snapshot JSON file.
        interval: Seconds between checks.
        on_drift: Callable receiving a list of drift dicts. Defaults to printing.
        stop_after: If set, stop after this many iterations (useful for testing).
    """
    if on_drift is None:
        def on_drift(entries: list[dict]) -> None:  # type: ignore[misc]
            if not entries:
                print("[stackfile watch] No drift detected.")
            else:
                print(f"[stackfile watch] Drift detected ({len(entries)} issue(s)):")
                for e in entries:
                    installed_label = e["installed"] or "not installed"
                    print(f"  [{e['section']}] {e['package']}: pinned={e['pinned']}, installed={installed_label} ({e['status']})")

    iterations = 0
    while True:
        try:
            snapshot = _load(path)
        except FileNotFoundError:
            raise WatchError(f"Snapshot file not found: {path}")
        except json.JSONDecodeError as exc:
            raise WatchError(f"Invalid JSON in snapshot: {exc}")

        pip = _installed_pip()
        npm = _installed_npm()
        brew = _installed_brew()

        drift = _detect_drift(snapshot, pip, npm, brew)
        on_drift(drift)

        iterations += 1
        if stop_after is not None and iterations >= stop_after:
            break

        time.sleep(interval)
