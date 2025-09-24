"""Simulated file loading routines for the Ragnar Mini OS boot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping


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

    def load_all(self) -> List[str]:
        """Simulate loading each file and return a log of the operations."""

        file_list = list(self.files)
        total = len(file_list)
        log: List[str] = []

        if total == 0:
            return ["No files registered for boot loading."]

        for index, relative_path in enumerate(file_list, start=1):
            absolute_path = self.root_directory / relative_path
            if absolute_path.exists():
                size = absolute_path.stat().st_size
                log.append(
                    f"Loaded {relative_path} [{index}/{total}] ({size} bytes cached)"
                )
            else:
                log.append(
                    f"Missing {relative_path} during boot load [{index}/{total}]"
                )

        return log


__all__ = ["FileLoader"]
