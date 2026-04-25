"""CLI subparser and handler for the split command."""

from __future__ import annotations

import argparse
import sys
from typing import List

from stackfile.split import SplitError, split_and_save


def add_split_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "split",
        help="Split a snapshot into one file per section.",
    )
    p.add_argument(
        "input",
        nargs="?",
        default="stackfile.json",
        help="Source snapshot file (default: stackfile.json).",
    )
    p.add_argument(
        "--output-dir",
        default=".",
        dest="output_dir",
        help="Directory to write split snapshots into (default: current dir).",
    )
    p.add_argument(
        "--sections",
        nargs="+",
        default=None,
        metavar="SECTION",
        help="Sections to split out (pip, npm, brew). Defaults to all.",
    )


def _handle_split(args: argparse.Namespace) -> int:
    try:
        written = split_and_save(
            input_path=args.input,
            output_dir=args.output_dir,
            sections=args.sections,
        )
    except SplitError as exc:
        print(f"split error: {exc}", file=sys.stderr)
        return 1

    for section, path in written.items():
        print(f"  {section:6s} -> {path}")
    print(f"Split into {len(written)} file(s) in '{args.output_dir}'.")
    return 0
