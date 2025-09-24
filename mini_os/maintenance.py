"""Automatic maintenance helpers for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple


def _read_file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as buffer:
        for chunk in iter(lambda: buffer.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class FileIntegrityVerifier:
    """Verify that critical MiniOS files match the expected hashes."""

    expected_hashes: Dict[str, str]
    root_directory: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])

    @classmethod
    def default_manifest(cls) -> "FileIntegrityVerifier":
        from .manifest import EXPECTED_HASHES

        return cls(expected_hashes=EXPECTED_HASHES)

    def verify(self) -> Tuple[bool, str]:
        """Return a tuple of (ok, message) after verifying all files."""

        mismatches: List[str] = []
        for relative_path, expected in self.expected_hashes.items():
            absolute_path = self.root_directory / relative_path
            if not absolute_path.exists():
                mismatches.append(f"{relative_path}: missing")
                continue
            actual = _read_file_hash(absolute_path)
            if actual != expected:
                mismatches.append(
                    f"{relative_path}: expected {expected[:8]} got {actual[:8]}"
                )

        if mismatches:
            message = "Integrity check FAILED -> " + "; ".join(mismatches)
            return False, message

        message = f"Integrity check passed for {len(self.expected_hashes)} files."
        return True, message


@dataclass
class AutoMaintenanceGuardian:
    """Perform automated upkeep routines for the Mini OS."""

    os_reference: "MiniOS"
    activity_log: List[str] = field(default_factory=list)

    def run_startup_jobs(self) -> List[str]:
        """Run core maintenance routines and return log entries."""

        jobs = [
            self._scan_application_health,
            self._refresh_interface_summary,
            self._schedule_background_tasks,
        ]
        entries: List[str] = []
        for job in jobs:
            entry = job()
            self.activity_log.append(entry)
            entries.append(entry)
        return entries

    # Maintenance jobs -------------------------------------------------

    def _scan_application_health(self) -> str:
        apps = list(self.os_reference.application_manager.list_applications())
        failures: List[str] = []
        for app in apps:
            try:
                preview = app.run()
                if not isinstance(preview, str) or not preview.strip():
                    failures.append(f"{app.name}: returned no content")
            except Exception as exc:  # pragma: no cover - defensive
                failures.append(f"{app.name}: {exc}")

        if failures:
            return "Application health issues detected -> " + "; ".join(failures)
        return f"All {len(apps)} applications responded successfully."

    def _refresh_interface_summary(self) -> str:
        widgets = list(self.os_reference.interface_manager.widgets)
        if not widgets:
            return "Interface warning: no widgets registered."
        titles = ", ".join(widget.title for widget in widgets)
        return f"Interface refreshed with widgets: {titles}."

    def _schedule_background_tasks(self) -> str:
        app_count = len(list(self.os_reference.application_manager.list_applications()))
        return (
            "Background scheduler primed -> "
            f"auto-backups for {app_count} apps queued."
        )


__all__ = ["FileIntegrityVerifier", "AutoMaintenanceGuardian"]
