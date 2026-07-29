from __future__ import annotations

from pathlib import Path

import pytest

from entrymap.cli import build_parser, main
from entrymap.scanner import EntryPointScanner


REPO_ROOT = Path("/root/WeeklyProjects/Week-19/entrymap") / "tests"
SAMPLE_PACKAGE = REPO_ROOT.parent


def test_parser_accepts_default_path() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.path == "."
    assert args.json is False
    assert args.summary is False


def test_positive_main_returns_zero(tmp_path: Path) -> None:
    rc = main([str(SAMPLE_PACKAGE)])
    assert rc == 0
    counts = EntryPointScanner(SAMPLE_PACKAGE).summary_counts()
    assert counts["entries"] >= 1


def test_negative_main_returns_nonzero_for_missing_path() -> None:
    fake = SAMPLE_PACKAGE / "does-not-exist-xyz"
    rc = main([str(fake)])
    assert rc != 0


def test_edge_case_empty_directory(tmp_path: Path) -> None:
    rc = main([str(tmp_path)])
    assert rc == 0
