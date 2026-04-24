"""CLI subparser and handler for the copy command."""
from __future__ import annotations

import argparse
import sys

from stackfile.copy import copy_and_save, CopyError


def add_copy_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "copy",
        help="Copy packages from one snapshot into another.",
    )
    p.add_argument("src", help="Source snapshot file.")
    p.add_argument("dst", help="Destination snapshot file.")
    p.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Write result to FILE instead of modifying dst in-place.",
    )
    p.add_argument(
        "--section",
        choices=["pip", "npm", "brew"],
        default=None,
        help="Limit copy to a specific section.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing packages in dst with versions from src.",
    )


def _handle_copy(args: argparse.Namespace) -> int:
    try:
        count = copy_and_save(
            args.src,
            args.dst,
            output_path=args.output,
            section=args.section,
            overwrite=args.overwrite,
        )
        dest_label = args.output or args.dst
        print(f"Copied {count} package(s) to {dest_label}.")
        return 0
    except CopyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
