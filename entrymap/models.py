from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class EntryPoint:
    group: str
    name: str
    module: str
    extra: str = ""
    relative: bool = False

    def formatted(self) -> str:
        target = f"{self.module}:{self.name}"
        target = f".{target}" if self.relative else target
        return f"{self.group}: {self.extra}{target}"


@dataclass(frozen=True)
class PackageRecord:
    path: Path
    pyproject_present: bool = False
    entry_points_groups: dict[str, list[EntryPoint]] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    @property
    def has_entry_points(self) -> bool:
        return bool(self.entry_points_groups)

    def render(self) -> str:
        status = "ok" if self.pyproject_present else "missing"
        header = f"[{status}] {self.path.as_posix()}"
        lines = [header]
        for group, entries in self.entry_points_groups.items():
            lines.append(f"  {group}:")
            for entry in entries:
                lines.append(f"    - {entry.formatted()}")
        for warning in self.warnings:
            lines.append(f"  ! {warning}")
        return "\n".join(lines)
