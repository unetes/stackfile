"""CLI sub-command handler for `stackfile filter`."""

from __future__ import annotations

import argparse
import json
import sys

from stackfile.filter import FilterError, filter_and_save


def add_filter_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("filter", help="Filter packages in a snapshot by criteria")
    p.add_argument("input", nargs="?", default="stackfile.json", help="Input snapshot (default: stackfile.json)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: overwrite input)")
    p.add_argument("--section", action="append", dest="sections", metavar="SECTION",
                   help="Restrict filtering to section(s): pip, npm, brew")
    p.add_argument("--name", default=None, help="Regex pattern to match package names")
    p.add_argument("--group", default=None, help="Only include packages with this group label")
    p.add_argument("--version", default=None, help="Regex pattern to match package versions")
    p.add_argument("--json", dest="as_json", action="store_true", help="Print filtered snapshot as JSON")


def _handle_filter(args: argparse.Namespace) -> int:
    output = args.output or args.input
    try:
        result = filter_and_save(
            args.input,
            output,
            sections=args.sections,
            name_pattern=args.name,
            group=args.group,
            version_pattern=args.version,
        )
    except FilterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        total = sum(len(result.get(s, [])) for s in ("pip", "npm", "brew"))
        print(f"Filtered snapshot written to {output} ({total} packages matched)")
    return 0
