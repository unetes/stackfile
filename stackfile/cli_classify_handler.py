"""Subparser and handler for the 'classify' CLI command."""
from __future__ import annotations

import argparse
import sys

from stackfile.classify import ClassifyError, classify_and_print


def add_classify_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "classify",
        help="Classify packages in a snapshot by category (dev/runtime/system/tool).",
    )
    p.add_argument(
        "--input", "-i",
        default="stackfile.json",
        metavar="FILE",
        help="Snapshot file to classify (default: stackfile.json).",
    )
    p.add_argument(
        "--section", "-s",
        default=None,
        choices=["pip", "npm", "brew"],
        help="Limit classification to a single section.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output results as JSON.",
    )


def _handle_classify(args: argparse.Namespace) -> int:
    fmt = "json" if args.json else "human"
    try:
        classify_and_print(args.input, section=args.section, fmt=fmt)
        return 0
    except ClassifyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
