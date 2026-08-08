<meta charset="utf-8">

<p align="left">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python Versions" />
  <img src="https://img.shields.io/badge/status-stable-green" alt="Status" />
  <img src="https://img.shields.io/badge/cli-entrypoint-green" alt="CLI" />
</p>

`entrymap` scans Python source directories for `pyproject.toml` files and reports the scripts / entry points each package registers.

## About

Notification scripts, plugins, and console-script entry points live in `pyproject.toml`, but it's hard to see which packages are registering them without opening every file. `entrymap` walks a directory tree, finds package roots with a `pyproject.toml`, parses the `project.entry-points` tables, and prints or emits a summary.

## Features

- Recursive package discovery via `pyproject.toml`
- Entry point group and target parsing with PEP 621 format
- Human-readable scannable report with per-package groups
- JSON report suitable for CI / downstream tooling
- Summary counts

## Installation

```bash
python -m pip install -e .
```

After installing, `entrymap` is on your PATH.

```bash
entrymap /path/to/repo
```

## Usage

Scan the current directory:

```bash
entrymap .
```

Scan another directory and request a count summary:

```bash
entrymap /workspace --summary
```

Emit JSON for automation:

```bash
entrymap /projects --json
```

### Options

- `path` — directory to scan (default `.`)
- `--json` — emit machine-readable JSON
- `--summary` — append total counts to the report

## Project structure

```text
entrymap/
  entrymap/
    __init__.py
    cli.py
    models.py
    scanner.py
  tests/
    test_scanner.py
    test_cli.py
  pyproject.toml
  README.md
```

## Development

```bash
ruff check entrymap tests
pytest
```

[entrymap](https://github.com/noahalexandercampbell/entrymap)

## Tags

`python`, `cli`, `entry-points`, `pyproject`, `developer-tools`, `audit`

## License

MIT
