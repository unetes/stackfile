"""CLI entry point for stackfile."""

import argparse
import sys
import json

from stackfile.snapshot import take_snapshot
from stackfile.restore import restore_snapshot
from stackfile.diff import diff_snapshots, format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackfile",
        description="Snapshot and restore your local dev environment.",
    )
    sub = parser.add_subparsers(dest="command")

    # snapshot
    snap = sub.add_parser("snapshot", help="Capture current environment")
    snap.add_argument("-o", "--output", default="stackfile.json")
    snap.add_argument("--skip-pip", action="store_true")
    snap.add_argument("--skip-npm", action="store_true")
    snap.add_argument("--skip-brew", action="store_true")

    # restore
    res = sub.add_parser("restore", help="Restore environment from snapshot")
    res.add_argument("-i", "--input", default="stackfile.json")
    res.add_argument("--skip-pip", action="store_true")
    res.add_argument("--skip-npm", action="store_true")
    res.add_argument("--skip-brew", action="store_true")

    # diff
    dif = sub.add_parser("diff", help="Diff two snapshot files")
    dif.add_argument("old", help="Path to older snapshot")
    dif.add_argument("new", help="Path to newer snapshot")
    dif.add_argument("--json", dest="as_json", action="store_true",
                     help="Output diff as JSON")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "snapshot":
        skip = set()
        if args.skip_pip:
            skip.add("pip")
        if args.skip_npm:
            skip.add("npm")
        if args.skip_brew:
            skip.add("brew")
        take_snapshot(args.output, skip=skip)
        print(f"Snapshot saved to {args.output}")
        return 0

    if args.command == "restore":
        skip = set()
        if args.skip_pip:
            skip.add("pip")
        if args.skip_npm:
            skip.add("npm")
        if args.skip_brew:
            skip.add("brew")
        restore_snapshot(args.input, skip=skip)
        print(f"Environment restored from {args.input}")
        return 0

    if args.command == "diff":
        diff = diff_snapshots(args.old, args.new)
        if args.as_json:
            print(json.dumps(diff, indent=2))
        else:
            print(format_diff(diff))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
