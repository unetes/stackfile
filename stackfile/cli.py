"""CLI entry point for stackfile."""
from __future__ import annotations

import argparse
import sys
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackfile",
        description="Snapshot and restore your local dev environment dependencies.",
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
    res.add_argument("input", nargs="?", default="stackfile.json")

    # diff
    diff = sub.add_parser("diff", help="Diff two snapshots")
    diff.add_argument("base")
    diff.add_argument("override")
    diff.add_argument("--json", action="store_true", dest="json_output")

    # export
    exp = sub.add_parser("export", help="Export snapshot to shell script or requirements.txt")
    exp.add_argument("input", nargs="?", default="stackfile.json")
    exp.add_argument("-o", "--output", default=None)
    exp.add_argument("--format", choices=["shell", "requirements"], default="shell")

    # validate
    val = sub.add_parser("validate", help="Validate a snapshot file")
    val.add_argument("input", nargs="?", default="stackfile.json")

    # merge
    mrg = sub.add_parser("merge", help="Merge two snapshots")
    mrg.add_argument("base")
    mrg.add_argument("override")
    mrg.add_argument("-o", "--output", default="stackfile.json")

    # pin
    pin = sub.add_parser("pin", help="Pin package versions in a snapshot")
    pin.add_argument("input", nargs="?", default="stackfile.json")
    pin.add_argument("-o", "--output", default=None)

    # search
    srch = sub.add_parser("search", help="Search for a package in a snapshot")
    srch.add_argument("query")
    srch.add_argument("input", nargs="?", default="stackfile.json")
    srch.add_argument("--case-sensitive", action="store_true")

    # audit
    aud = sub.add_parser("audit", help="Audit snapshot for outdated packages")
    aud.add_argument("input", nargs="?", default="stackfile.json")
    aud.add_argument("--json", action="store_true", dest="json_output")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "snapshot":
        from stackfile.snapshot import capture_snapshot, save_snapshot
        data = capture_snapshot(skip_pip=args.skip_pip, skip_npm=args.skip_npm, skip_brew=args.skip_brew)
        save_snapshot(data, args.output)
        print(f"Snapshot saved to {args.output}")
        return 0

    if args.command == "restore":
        from stackfile.restore import restore_snapshot
        restore_snapshot(args.input)
        return 0

    if args.command == "diff":
        from stackfile.diff import diff_snapshots, format_diff
        results = diff_snapshots(args.base, args.override)
        fmt = "json" if args.json_output else "human"
        print(format_diff(results, fmt=fmt))
        return 0

    if args.command == "export":
        from stackfile.export import export_snapshot
        export_snapshot(args.input, output=args.output, fmt=args.format)
        return 0

    if args.command == "validate":
        from stackfile.validate import validate_or_exit
        return validate_or_exit(args.input)

    if args.command == "merge":
        from stackfile.merge import merge_and_save
        merge_and_save(args.base, args.override, args.output)
        print(f"Merged snapshot saved to {args.output}")
        return 0

    if args.command == "pin":
        from stackfile.pin import pin_snapshot
        pin_snapshot(args.input, output=args.output)
        return 0

    if args.command == "search":
        from stackfile.search import search_and_print
        return search_and_print(args.input, args.query, case_sensitive=args.case_sensitive)

    if args.command == "audit":
        from stackfile.audit import audit_snapshot, format_audit
        results = audit_snapshot(args.input)
        fmt = "json" if args.json_output else "human"
        print(format_audit(results, fmt=fmt))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
