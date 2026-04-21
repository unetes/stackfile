"""Remove packages from a snapshot that are no longer installed locally."""

import json
import subprocess
from pathlib import Path


class PruneError(Exception):
    pass


def _load(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise PruneError(f"Cannot load snapshot: {exc}") from exc


def _save(data: dict, path: str) -> None:
    Path(path).write_text(json.dumps(data, indent=2))


def _installed_pip() -> set:
    try:
        out = subprocess.check_output(["pip", "list", "--format=json"], text=True)
        return {pkg["name"].lower() for pkg in json.loads(out)}
    except Exception:
        return set()


def _installed_npm() -> set:
    try:
        out = subprocess.check_output(
            ["npm", "list", "-g", "--depth=0", "--json"], text=True
        )
        deps = json.loads(out).get("dependencies", {})
        return {name.lower() for name in deps}
    except Exception:
        return set()


def _installed_brew() -> set:
    try:
        out = subprocess.check_output(["brew", "list", "--formula"], text=True)
        return {line.strip().lower() for line in out.splitlines() if line.strip()}
    except Exception:
        return set()


def prune_snapshot(input_path: str, output_path: str | None = None) -> dict:
    """Remove packages not found in the local environment and return the pruned snapshot."""
    snapshot = _load(input_path)

    installers = {
        "pip": _installed_pip,
        "npm": _installed_npm,
        "brew": _installed_brew,
    }

    pruned_counts: dict[str, int] = {}

    for section, get_installed in installers.items():
        packages = snapshot.get(section, {}).get("packages", [])
        if not packages:
            continue
        installed = get_installed()
        kept = [p for p in packages if p.get("name", "").lower() in installed]
        removed = len(packages) - len(kept)
        if removed:
            pruned_counts[section] = removed
        snapshot[section]["packages"] = kept

    dest = output_path or input_path
    _save(snapshot, dest)
    return {"snapshot": snapshot, "pruned": pruned_counts}
