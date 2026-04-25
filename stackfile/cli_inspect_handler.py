"""Subparser and handler for the 'inspect' CLI command."""

import argparse
from stackfile.inspect import inspect_and_print


def add_inspect_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "inspect",
        help="Show detailed info about a specific package in a snapshot",
    )
    p.add_argument(
        "package",
        help="Name of the package to inspect",
    )
    p.add_argument(
        "--input", "-i",
        default="stackfile.json",
        metavar="FILE",
        help="Snapshot file to inspect (default: stackfile.json)",
    )
    p.add_argument(
        "--section", "-s",
        choices=["pip", "npm", "brew"],
        default=None,
        help="Limit search to a specific section",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )


def _handle_inspect(args: argparse.Namespace) -> int:
    fmt = "json" if args.json_output else "human"
    return inspect_and_print(
        args.input,
        args.package,
        section=args.section,
        fmt=fmt,
    )
