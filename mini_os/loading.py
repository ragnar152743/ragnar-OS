"""Simulated file loading routines for the Ragnar Mini OS boot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping


@dataclass
class FileLoadRecord:
    """Record describing a simulated file load during boot."""

    path: str
    index: int
    total: int
    bytes_cached: int | None


@dataclass
class FileLoader:
    """Load key MiniOS files during boot to mimic a startup sequence."""

    files: Iterable[str]
    root_directory: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[1]
    )

    @classmethod
    def from_manifest(cls, manifest: Mapping[str, str]) -> "FileLoader":
        """Build a loader from a manifest map of file paths to hashes."""

        ordered_files = sorted(manifest.keys())
        return cls(files=ordered_files)

    def load_all(self) -> List[FileLoadRecord]:
        """Simulate loading each file and return structured load records."""

        file_list = list(self.files)
        total = len(file_list)
        log: List[FileLoadRecord] = []

        if total == 0:
            return []

        for index, relative_path in enumerate(file_list, start=1):
            absolute_path = self.root_directory / relative_path
            if absolute_path.exists():
                size = absolute_path.stat().st_size
                record = FileLoadRecord(
                    path=relative_path,
                    index=index,
                    total=total,
                    bytes_cached=size,
                )
            else:
                record = FileLoadRecord(
                    path=relative_path,
                    index=index,
                    total=total,
                    bytes_cached=None,
                )
            log.append(record)

        return log


__all__ = ["FileLoader", "FileLoadRecord"]
