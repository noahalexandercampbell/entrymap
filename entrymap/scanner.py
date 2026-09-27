from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator

from entrymap.models import EntryPoint, PackageRecord

ENTRY_POINT_SECTION_RE = re.compile(r"^\[project\.entry-points\.([^\]]+)\]$", re.IGNORECASE)
ENTRY_POINT_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*=\s*(.+)$")
TOML_SECTION_RE = re.compile(r"^\[[^\]]+\]$")


def parse_entry_points_table(text: str) -> dict[str, list[EntryPoint]]:
    groups: dict[str, list[EntryPoint]] = {}
    current_group: str | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if TOML_SECTION_RE.match(stripped):
            current_group = None
            match_group = ENTRY_POINT_SECTION_RE.match(stripped)
            if match_group:
                current_group = match_group.group(1)
                groups.setdefault(current_group, [])
            continue
        if current_group is None:
            continue
        match_entry = ENTRY_POINT_RE.match(stripped)
        if match_entry:
            name = match_entry.group(1)
            target = match_entry.group(2).strip().strip('"').strip("'")
            module_part, relative = _module_for_target(target)
            if ":" in module_part:
                module = module_part.split(":", maxsplit=1)[0]
                entry_name = module_part.split(":", maxsplit=1)[1] or name
            else:
                module = module_part
                entry_name = name
            groups[current_group].append(
                EntryPoint(
                    group=current_group,
                    name=entry_name,
                    module=module,
                    relative=relative,
                )
            )

    return groups


def _module_for_target(target: str) -> tuple[str, bool]:
    target = target.strip().strip('"').strip("'")
    if target.startswith("."):
        module = target[1:]
        relative = True
    else:
        module = target
        relative = False
    if ":" in module:
        module_part = module.split(":", maxsplit=1)[0]
    else:
        module_part = module
    return module_part, relative


def iter_python_packages(root: Path) -> Iterator[Path]:
    root_pyproject = root / "pyproject.toml"
    if root_pyproject.exists() and root.is_dir():
        yield root.resolve()

    for path in root.rglob("pyproject.toml"):
        resolved = path.resolve()
        parent = resolved.parent
        if parent == root:
            continue
        if parent.name == ".git":
            continue
        if parent.name == "__pycache__":
            continue
        yield parent


class EntryPointScanner:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.packages = list(self._scan())

    def _scan(self) -> Iterable[PackageRecord]:
        warnings = []

        for package_path in iter_python_packages(self.root):
            pyproject_path = package_path / "pyproject.toml"
            if not pyproject_path.exists():
                yield PackageRecord(path=package_path)
                continue

            text = pyproject_path.read_text(encoding="utf-8", errors="ignore")
            groups = parse_entry_points_table(text)
            yield PackageRecord(path=package_path, pyproject_present=True, entry_points_groups=groups, warnings=tuple(warnings))

    def formatted_text(self) -> str:
        if not self.packages:
            return "No Python package directories with a pyproject.toml were found."
        return "\n".join(record.render() for record in self.packages)

    def summary_counts(self) -> dict[str, int]:
        packages = len(self.packages)
        groups = 0
        entries = 0
        for record in self.packages:
            if record.has_entry_points:
                groups += len(record.entry_points_groups)
                entries += sum(len(items) for items in record.entry_points_groups.values())
        return {"packages": packages, "groups": groups, "entries": entries}
