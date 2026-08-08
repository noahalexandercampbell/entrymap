from __future__ import annotations

from pathlib import Path

from entrymap.scanner import EntryPointScanner, parse_entry_points_table

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_parse_entry_points_table_basic() -> None:
    text = """
[project]
name = "demo"

[project.entry-points.entrymap.cli]
serve = "pkg.main:main"
serve-debug = ".cli:serve"
orphan = "utils.helpers"

[project.entry-points.gui]
start = "pkg.ui:MainWindow.start"
"""
    groups = parse_entry_points_table(text)
    assert "entrymap.cli" in groups
    assert "gui" in groups
    assert len(groups["entrymap.cli"]) == 3
    assert len(groups["gui"]) == 1

    first, second, third = groups["entrymap.cli"]
    assert first.group == "entrymap.cli"
    assert first.name == "serve"
    assert first.module == "pkg.main"
    assert first.relative is False
    assert first.formatted() == "entrymap.cli: pkg.main:serve"

    assert second.name == "serve-debug"
    assert second.module == "cli"
    assert second.relative is True
    assert second.formatted() == "entrymap.cli: .cli:serve-debug"

    assert third.name == "orphan"
    assert third.module == "utils.helpers"
    assert third.relative is False


def test_scanner_discovers_local_package() -> None:
    scanner = EntryPointScanner(REPO_ROOT)
    paths = {record.path.resolve() for record in scanner.packages}
    assert REPO_ROOT.resolve() in paths


def test_scanner_reports_entry_points() -> None:
    scanner = EntryPointScanner(REPO_ROOT)
    entries = [
        entry
        for record in scanner.packages
        for items in record.entry_points_groups.values()
        for entry in items
    ]
    assert len(entries) >= 1
    names = {entry.name for entry in entries}
    assert "entrymap" in names


def test_summary_counts_are_nonzero() -> None:
    scanner = EntryPointScanner(REPO_ROOT)
    counts = scanner.summary_counts()
    assert counts["packages"] >= 1
    assert counts["entries"] >= 1
    assert counts["groups"] >= 1


def test_json_output_includes_expected_keys(tmp_path: Path) -> None:
    import json
    import os
    import subprocess
    import sys

    output = subprocess.check_output([sys.executable, "-m", "entrymap.cli", str(tmp_path), "--json"])
    payload = json.loads(output)
    assert "packages" in payload
    assert "counts" in payload
