"""Track and display snapshot history from a log file."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

DEFAULT_HISTORY_FILE = "stackfile_history.jsonl"


class HistoryError(Exception):
    pass


def _load_history(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise HistoryError(f"Corrupt history entry: {e}")
    return entries


def record_event(event: str, snapshot_path: str, history_path: str = DEFAULT_HISTORY_FILE) -> None:
    """Append a history event to the log."""
    entry = {
        "event": event,
        "snapshot": snapshot_path,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    with open(history_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def list_history(history_path: str = DEFAULT_HISTORY_FILE) -> List[Dict[str, Any]]:
    """Return all recorded history entries."""
    return _load_history(history_path)


def clear_history(history_path: str = DEFAULT_HISTORY_FILE) -> None:
    """Remove all history entries."""
    if os.path.exists(history_path):
        os.remove(history_path)


def format_history(entries: List[Dict[str, Any]]) -> str:
    """Format history entries as a human-readable string."""
    if not entries:
        return "No history recorded."
    lines = []
    for e in entries:
        lines.append(f"[{e.get('timestamp', '?')}] {e.get('event', '?')} -> {e.get('snapshot', '?')}")
    return "\n".join(lines)
