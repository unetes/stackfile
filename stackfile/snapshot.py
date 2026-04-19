"""Snapshot module: captures the current dev environment dependencies."""

import subprocess
import sys
import json
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_TOOLS = ["pip", "npm", "brew"]


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command {' '.join(cmd)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def capture_pip() -> list[dict]:
    output = _run([sys.executable, "-m", "pip", "list", "--format=json"])
    return json.loads(output)


def capture_npm() -> list[dict]:
    output = _run(["npm", "list", "-g", "--depth=0", "--json"])
    data = json.loads(output)
    deps = data.get("dependencies", {})
    return [{"name": name, "version": info.get("version", "unknown")}
            for name, info in deps.items()]


def capture_brew() -> list[dict]:
    output = _run(["brew", "list", "--versions"])
    packages = []
    for line in output.splitlines():
        parts = line.split()
        if parts:
            packages.append({"name": parts[0], "version": parts[1] if len(parts) > 1 else "unknown"})
    return packages


CAPTURERS = {
    "pip": capture_pip,
    "npm": capture_npm,
    "brew": capture_brew,
}


def load_snapshot(path: str = "stackfile.json") -> dict:
    """Load and return a previously saved snapshot from the given path.

    Raises:
        FileNotFoundError: if the snapshot file does not exist.
        ValueError: if the file content is not valid JSON.
    """
    snapshot_path = Path(path)
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    try:
        return json.loads(snapshot_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in snapshot file '{path}': {exc}") from exc


def take_snapshot(tools: list[str] | None = None, output_path: str = "stackfile.json") -> dict:
    """Capture dependencies for the given tools and write to output_path."""
    tools = tools or SUPPORTED_TOOLS
    snapshot = {
        "version": "1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dependencies": {},
    }

    for tool in tools:
        if tool not in CAPTURERS:
            print(f"[warning] Unknown tool '{tool}', skipping.", file=sys.stderr)
            continue
        try:
            packages = CAPTURERS[tool]()
            snapshot["dependencies"][tool] = packages
            print(f"[snapshot] Captured {len(packages)} {tool} package(s).")
        except (RuntimeError, FileNotFoundError) as exc:
            print(f"[warning] Could not capture {tool}: {exc}", file=sys.stderr)

    Path(output_path).write_text(json.dumps(snapshot, indent=2))
    print(f"[snapshot] Saved to {output_path}")
    return snapshot
