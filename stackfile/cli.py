"""CLI entry-point for stackfile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stackfile", description="Snapshot and restore dev dependencies")
    sub = parser.add_subparsers(dest="command")

    # snapshot
    snap = sub.add_parser("snapshot", help="Capture current environment")
    snap.add_argument("--output", default="stack.json")
    snap.add_argument("--skip-pip", action="store_true")
    snap.add_argument("--skip-npm", action="store_true")
    snap.add_argument("--skip-brew", action="store_true")

    # restore
    rst = sub.add_parser("restore", help="Restore environment from snapshot")
    rst.add_argument("--input", default="stack.json")

    # diff
    dff = sub.add_parser("diff", help="Diff two snapshots")
    dff.add_argument("base")
    dff.add_argument("other")
    dff.add_argument("--json", dest="as_json", action="store_true")

    # export
    exp = sub.add_parser("export", help="Export snapshot")
    exp.add_argument("--input", default="stack.json")
    exp.add_argument("--format", dest="fmt", choices=["shell", "requirements"], default="shell")
    exp.add_argument("--output", default=None)

    # validate
    val = sub.add_parser("validate", help="Validate a snapshot file")
    val.add_argument("--input", default="stack.json")

    # merge
    mrg = sub.add_parser("merge", help="Merge two snapshots")
    mrg.add_argument("base")
    mrg.add_argument("override")
    mrg.add_argument("--output", default="merged.json")

    # pin
    pin = sub.add_parser("pin", help="Pin package versions")
    pin.add_argument("--input", default="stack.json")
    pin.add_argument("--output", default=None)

    # search
    srch = sub.add_parser("search", help="Search packages in snapshot")
    srch.add_argument("query")
    srch.add_argument("--input", default="stack.json")
    srch.add_argument("--case-sensitive", action="store_true")

    # audit
    aud = sub.add_parser("audit", help="Audit installed vs snapshot")
    aud.add_argument("--input", default="stack.json")
    aud.add_argument("--json", dest="as_json", action="store_true")

    # tag
    tag = sub.add_parser("tag", help="Manage snapshot tags")
    tag_sub = tag.add_subparsers(dest="tag_command")
    tag_add = tag_sub.add_parser("add")
    tag_add.add_argument("tag")
    tag_add.add_argument("--input", default="stack.json")
    tag_rm = tag_sub.add_parser("remove")
    tag_rm.add_argument("tag")
    tag_rm.add_argument("--input", default="stack.json")
    tag_ls = tag_sub.add_parser("list")
    tag_ls.add_argument("--input", default="stack.json")

    # compare
    cmp = sub.add_parser("compare", help="Compare two snapshots")
    cmp.add_argument("a")
    cmp.add_argument("b")
    cmp.add_argument("--json", dest="as_json", action="store_true")

    # history
    hist = sub.add_parser("history", help="Manage operation history")
    hist_sub = hist.add_subparsers(dest="history_command")
    hist_sub.add_parser("list")
    hist_sub.add_parser("clear")

    # lint
    lnt = sub.add_parser("lint", help="Lint a snapshot")
    lnt.add_argument("--input", default="stack.json")

    # freeze
    frz = sub.add_parser("freeze", help="Freeze installed versions into snapshot")
    frz.add_argument("--input", default="stack.json")
    frz.add_argument("--output", default=None)

    # doctor
    sub.add_parser("doctor", help="Check environment health")

    # template
    tmpl = sub.add_parser("template", help="Generate a blank snapshot template")
    tmpl.add_argument("--preset", default=None)
    tmpl.add_argument("--output", default="stack.json")
    tmpl.add_argument("--description", default="")

    # profile
    prof = sub.add_parser("profile", help="Manage named environment profiles")
    prof_sub = prof.add_subparsers(dest="profile_command")

    prof_save = prof_sub.add_parser("save", help="Save current snapshot as a named profile")
    prof_save.add_argument("name")
    prof_save.add_argument("--input", default="stack.json")
    prof_save.add_argument("--profiles-dir", default=None)

    prof_load = prof_sub.add_parser("load", help="Restore a named profile to a snapshot file")
    prof_load.add_argument("name")
    prof_load.add_argument("--output", default="stack.json")
    prof_load.add_argument("--profiles-dir", default=None)

    prof_ls = prof_sub.add_parser("list", help="List saved profiles")
    prof_ls.add_argument("--profiles-dir", default=None)

    prof_del = prof_sub.add_parser("delete", help="Delete a saved profile")
    prof_del.add_argument("name")
    prof_del.add_argument("--profiles-dir", default=None)

    prof_show = prof_sub.add_parser("show", help="Show contents of a profile")
    prof_show.add_argument("name")
    prof_show.add_argument("--profiles-dir", default=None)

    return parser


def _profiles_dir_arg(raw: str | None):
    from pathlib import Path as _P
    return _P(raw) if raw else None


def main(argv=None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "snapshot":
        from stackfile.snapshot import capture_snapshot
        capture_snapshot(
            output=args.output,
            skip_pip=args.skip_pip,
            skip_npm=args.skip_npm,
            skip_brew=args.skip_brew,
        )
        return 0

    if args.command == "restore":
        from stackfile.restore import restore_snapshot
        restore_snapshot(args.input)
        return 0

    if args.command == "diff":
        import json
        from stackfile.diff import diff_snapshots, format_diff
        result = diff_snapshots(args.base, args.other)
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            print(format_diff(result))
        return 0

    if args.command == "export":
        from stackfile.export import export_snapshot
        export_snapshot(args.input, fmt=args.fmt, output=args.output)
        return 0

    if args.command == "validate":
        from stackfile.validate import validate_or_exit
        return validate_or_exit(args.input)

    if args.command == "merge":
        from stackfile.merge import merge_and_save
        merge_and_save(args.base, args.override, args.output)
        return 0

    if args.command == "pin":
        from stackfile.pin import pin_snapshot
        pin_snapshot(args.input, args.output)
        return 0

    if args.command == "search":
        from stackfile.search import search_and_print
        search_and_print(args.input, args.query, case_sensitive=args.case_sensitive)
        return 0

    if args.command == "audit":
        import json
        from stackfile.audit import audit_snapshot
        result = audit_snapshot(args.input)
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            for section, items in result.items():
                for item in items:
                    status = "OK" if item.get("up_to_date") else "OUTDATED"
                    print(f"[{section}] {item['name']}: {status}")
        return 0

    if args.command == "tag":
        from stackfile.tag import add_tag, remove_tag, list_tags
        if args.tag_command == "add":
            add_tag(args.input, args.tag)
        elif args.tag_command == "remove":
            remove_tag(args.input, args.tag)
        elif args.tag_command == "list":
            for t in list_tags(args.input):
                print(t)
        return 0

    if args.command == "compare":
        import json
        from stackfile.compare import compare_snapshots, format_compare
        result = compare_snapshots(args.a, args.b)
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            print(format_compare(result))
        return 0

    if args.command == "history":
        from stackfile.history import list_history, clear_history
        if args.history_command == "list":
            entries = list_history()
            if not entries:
                print("No history recorded.")
            for e in entries:
                print(e)
        elif args.history_command == "clear":
            clear_history()
        return 0

    if args.command == "lint":
        from stackfile.lint import lint_and_print
        return lint_and_print(args.input)

    if args.command == "freeze":
        from stackfile.freeze import freeze_snapshot
        freeze_snapshot(args.input, args.output)
        return 0

    if args.command == "doctor":
        from stackfile.doctor import run_doctor
        run_doctor()
        return 0

    if args.command == "template":
        from stackfile.template import save_template
        save_template(args.output, preset=args.preset, description=args.description)
        return 0

    if args.command == "profile":
        from stackfile.profile import (
            save_profile, load_profile, list_profiles, delete_profile, show_profile, ProfileError
        )
        import json as _json
        pd = _profiles_dir_arg(args.profiles_dir)
        try:
            if args.profile_command == "save":
                dest = save_profile(args.name, Path(args.input), pd)
                print(f"Profile '{args.name}' saved to {dest}")
            elif args.profile_command == "load":
                out = load_profile(args.name, Path(args.output), pd)
                print(f"Profile '{args.name}' loaded to {out}")
            elif args.profile_command == "list":
                names = list_profiles(pd)
                if not names:
                    print("No profiles saved.")
                else:
                    for n in names:
                        print(n)
            elif args.profile_command == "delete":
                delete_profile(args.name, pd)
                print(f"Profile '{args.name}' deleted.")
            elif args.profile_command == "show":
                data = show_profile(args.name, pd)
                print(_json.dumps(data, indent=2))
            else:
                parser.parse_args(["profile", "--help"])
                return 1
        except ProfileError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
