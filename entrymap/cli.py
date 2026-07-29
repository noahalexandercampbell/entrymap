from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from entrymap.scanner import EntryPointScanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="entrymap",
        description="Scan Python source trees and map package entry points from pyproject.toml."
    )
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan for package trees.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text.")
    parser.add_argument("--summary", action="store_true", help="Append count summary after the report.")
    return parser


def format_counts(counts: dict[str, int]) -> str:
    return f"packages={counts['packages']}, groups={counts['groups']}, entries={counts['entries']}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = Path(args.path)
    if not path.exists():
        sys.stderr.write(f"error: path does not exist: {path}\n")
        return 1
    if not path.is_dir():
        sys.stderr.write(f"error: expected a directory: {path}\n")
        return 1

    scanner = EntryPointScanner(path)
    report = scanner.formatted_text()
    counts = scanner.summary_counts()

    if args.json:
        payload = {
            "packages": [
                {
                    "path": str(record.path),
                    "entry_points_groups": {
                        group: [
                            {"name": entry.name, "module": entry.module, "relative": entry.relative}
                            for entry in entries
                        ]
                        for group, entries in record.entry_points_groups.items()
                    },
                }
                for record in scanner.packages
                if record.has_entry_points
            ],
            "counts": counts,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(report)
        if args.summary:
            print(f"\nsummary: {format_counts(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
