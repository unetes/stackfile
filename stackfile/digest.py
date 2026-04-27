"""Compute a deterministic digest (hash) of a snapshot for integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


class DigestError(Exception):
    pass


def _load(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise DigestError(f"File not found: {path}")
    with p.open() as fh:
        return json.load(fh)


def _canonical(data: Dict[str, Any]) -> bytes:
    """Return a stable JSON encoding suitable for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def compute_digest(data: Dict[str, Any], algorithm: str = "sha256") -> str:
    """Return a hex digest of *data* using *algorithm*."""
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise DigestError(f"Unsupported algorithm: {algorithm}") from exc
    h.update(_canonical(data))
    return h.hexdigest()


def digest_snapshot(path: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """Load *path* and return a result dict with the hex digest and algorithm."""
    data = _load(path)
    hex_digest = compute_digest(data, algorithm)
    return {
        "path": path,
        "algorithm": algorithm,
        "digest": hex_digest,
    }


def verify_digest(path: str, expected: str, algorithm: str = "sha256") -> bool:
    """Return True if the digest of *path* matches *expected*."""
    result = digest_snapshot(path, algorithm)
    return result["digest"] == expected


def format_digest(result: Dict[str, Any], fmt: str = "human") -> str:
    if fmt == "json":
        return json.dumps(result, indent=2)
    return f"{result['algorithm']}:{result['digest']}  {result['path']}"
