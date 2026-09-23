"""Command-line entry point for read-only CSV triage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_paths
from .fixtures import write_fixtures
from .reconcile import reconcile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="icarus-csv-evidence")
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="Hash and check CSV structure without modifying source files")
    scan.add_argument("paths", nargs="+", help="CSV files or directories")
    scan.add_argument("--delimiter", choices=[",", ";", "\t"], default=None)
    scan.add_argument("--output", type=Path, help="Write a local JSON report; keep it out of Git")
    fixtures = commands.add_parser("fixtures", help="Create synthetic importer regression fixtures")
    fixtures.add_argument("output_dir", type=Path)
    fixtures.add_argument("--overwrite", action="store_true", help="Allow replacing generated fixture names")
    compare = commands.add_parser("reconcile", help="Compare AION and NEXUS inventory JSON by raw hash")
    compare.add_argument("aion_manifest", type=Path)
    compare.add_argument("nexus_catalog", type=Path)
    compare.add_argument("--output", type=Path, help="Write a local JSON report; keep it out of Git")
    args = parser.parse_args(argv)
    if args.command == "fixtures":
        try:
            print(write_fixtures(args.output_dir, overwrite=args.overwrite))
        except (FileExistsError, OSError) as exc:
            parser.error(str(exc))
        return 0
    if args.command == "reconcile":
        try:
            report = reconcile(args.aion_manifest, args.nexus_catalog)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        serialized = json.dumps(report, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + "\n", encoding="utf-8")
            print(args.output.resolve())
        else:
            print(serialized)
        return 0
    try:
        report = audit_paths(args.paths, delimiter=args.delimiter)
    except (FileNotFoundError, ValueError, OSError) as exc:
        parser.error(str(exc))
    serialized = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
        print(args.output.resolve())
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
