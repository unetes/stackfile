"""CLI handler for the dedupe command (wired into cli.py via build_parser)."""

from __future__ import annotations

import sys

from stackfile.dedupe import dedupe_snapshot, DedupeError


def add_dedupe_subparser(subparsers) -> None:
    """Register the 'dedupe' subcommand on *subparsers*."""
    p = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate package entries from a snapshot.",
    )
    p.add_argument(
        "input",
        nargs="?",
        default="stackfile.json",
        help="Path to snapshot file (default: stackfile.json)",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write result to this file instead of overwriting input.",
    )
    p.add_argument(
        "--section",
        "-s",
        action="append",
        dest="sections",
        metavar="SECTION",
        help="Limit deduplication to this section (repeatable).",
    )
    p.set_defaults(func=_handle_dedupe)


def _handle_dedupe(args) -> int:
    try:
        report = dedupe_snapshot(
            input_path=args.input,
            output_path=args.output,
            sections=args.sections or None,
        )
    except DedupeError as exc:
        print(f"dedupe: error: {exc}", file=sys.stderr)
        return 1

    total_removed = sum(report.values())
    if total_removed == 0:
        print("No duplicates found.")
    else:
        for section, count in report.items():
            if count:
                print(f"  {section}: removed {count} duplicate(s)")
        dest = args.output or args.input
        print(f"Saved to {dest}")
    return 0
