"""CLI entry point for stackfile."""
import argparse
import sys
from stackfile.snapshot import take_snapshot
from stackfile.restore import restore_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackfile",
        description="Snapshot and restore your local dev environment dependencies.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # snapshot
    snap_parser = subparsers.add_parser("snapshot", help="Capture current environment.")
    snap_parser.add_argument(
        "-o",
        "--output",
        default="stackfile.json",
        metavar="FILE",
        help="Output file path (default: stackfile.json).",
    )
    snap_parser.add_argument(
        "--no-pip", action="store_true", help="Skip pip packages."
    )
    snap_parser.add_argument(
        "--no-npm", action="store_true", help="Skip npm global packages."
    )
    snap_parser.add_argument(
        "--no-brew", action="store_true", help="Skip Homebrew packages."
    )

    # restore
    restore_parser = subparsers.add_parser("restore", help="Restore environment from snapshot.")
    restore_parser.add_argument(
        "input",
        nargs="?",
        default="stackfile.json",
        metavar="FILE",
        help="Snapshot file to restore from (default: stackfile.json).",
    )
    restore_parser.add_argument(
        "--no-pip", action="store_true", help="Skip pip packages."
    )
    restore_parser.add_argument(
        "--no-npm", action="store_true", help="Skip npm global packages."
    )
    restore_parser.add_argument(
        "--no-brew", action="store_true", help="Skip Homebrew packages."
    )

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "snapshot":
        skip = set()
        if args.no_pip:
            skip.add("pip")
        if args.no_npm:
            skip.add("npm")
        if args.no_brew:
            skip.add("brew")
        take_snapshot(output=args.output, skip=skip)
        print(f"Snapshot saved to {args.output}")
        return 0

    if args.command == "restore":
        skip = set()
        if args.no_pip:
            skip.add("pip")
        if args.no_npm:
            skip.add("npm")
        if args.no_brew:
            skip.add("brew")
        restore_snapshot(input_file=args.input, skip=skip)
        print(f"Environment restored from {args.input}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
