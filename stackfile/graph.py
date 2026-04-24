"""graph.py — Build and render a dependency graph from a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GraphError(Exception):
    """Raised when graph generation fails."""


def _load(path: str) -> dict[str, Any]:
    """Load and return a snapshot dict from *path*."""
    p = Path(path)
    if not p.exists():
        raise GraphError(f"Snapshot file not found: {path}")
    with p.open() as fh:
        return json.load(fh)


def _packages_for_section(snapshot: dict[str, Any], section: str) -> list[dict[str, Any]]:
    """Return the package list for *section*, or an empty list."""
    return snapshot.get(section, {}).get("packages", [])


def build_graph(snapshot: dict[str, Any]) -> dict[str, list[str]]:
    """Return an adjacency-list graph of package → dependencies.

    Each package node lists the packages it *depends on* according to the
    optional ``"dependencies"`` field stored on individual package entries.
    Packages without that field are still included as leaf nodes.

    The node key format is ``"<section>:<name>"`` so that identically-named
    packages in different sections (e.g. pip vs npm) remain distinct.
    """
    graph: dict[str, list[str]] = {}

    for section in ("pip", "npm", "brew"):
        for pkg in _packages_for_section(snapshot, section):
            name = pkg.get("name", "")
            if not name:
                continue
            node = f"{section}:{name}"
            raw_deps: list[str] = pkg.get("dependencies") or []
            # Normalise deps to the same "section:name" format when the caller
            # has already stored them that way; otherwise prefix with the same
            # section as the parent package.
            resolved: list[str] = []
            for dep in raw_deps:
                if ":" in dep:
                    resolved.append(dep)
                else:
                    resolved.append(f"{section}:{dep}")
            graph[node] = resolved

    return graph


def format_graph(
    graph: dict[str, list[str]],
    as_json: bool = False,
) -> str:
    """Render *graph* as a human-readable tree or JSON string.

    Human-readable example::

        pip:requests
          └─ pip:urllib3
          └─ pip:certifi
        npm:axios (no dependencies)
    """
    if as_json:
        return json.dumps(graph, indent=2)

    if not graph:
        return "(empty graph)"

    lines: list[str] = []
    for node, deps in sorted(graph.items()):
        lines.append(node)
        if deps:
            for i, dep in enumerate(deps):
                connector = "└─" if i == len(deps) - 1 else "├─"
                lines.append(f"  {connector} {dep}")
        else:
            lines[-1] += "  (no dependencies)"
    return "\n".join(lines)


def graph_snapshot(
    input_path: str,
    as_json: bool = False,
    section: str | None = None,
) -> str:
    """Load *input_path*, build its dependency graph, and return a formatted string.

    Args:
        input_path: Path to the snapshot JSON file.
        as_json:    When *True* return raw JSON instead of the tree view.
        section:    If given, restrict output to packages in that section only
                    (``"pip"``, ``"npm"``, or ``"brew"``).

    Returns:
        Formatted string representation of the graph.

    Raises:
        GraphError: If the file cannot be loaded.
    """
    snapshot = _load(input_path)
    graph = build_graph(snapshot)

    if section:
        prefix = f"{section}:"
        graph = {k: v for k, v in graph.items() if k.startswith(prefix)}

    return format_graph(graph, as_json=as_json)
