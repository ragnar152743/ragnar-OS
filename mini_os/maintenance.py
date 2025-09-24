"""Automatic maintenance helpers for the Ragnar Mini OS."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from dataclasses import dataclass, field

from .localization import LanguageManager

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
    language_manager: LanguageManager | None = None

    @classmethod
    def default_manifest(cls, language_manager: LanguageManager | None = None) -> "FileIntegrityVerifier":
        from .manifest import EXPECTED_HASHES

        return cls(expected_hashes=EXPECTED_HASHES, language_manager=language_manager)

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

        translator = self.language_manager.translate if self.language_manager else None
        if mismatches:
            details = "; ".join(mismatches)
            if translator:
                message = translator("integrity_fail_prefix", details=details)
            else:
                message = "Integrity check FAILED -> " + details
            return False, message

        count = len(self.expected_hashes)
        if translator:
            message = translator("integrity_pass", count=count)
        else:
            message = f"Integrity check passed for {count} files."
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
        translator = self.os_reference.language_manager.translate
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
            return translator("maintenance_apps_failure", details="; ".join(failures))
        return translator("maintenance_apps_ok", count=len(apps))

    def _refresh_interface_summary(self) -> str:
        widgets = list(self.os_reference.interface_manager.widgets)
        translator = self.os_reference.language_manager.translate
        if not widgets:
            return translator("maintenance_interface_missing")
        titles = ", ".join(widget.title for widget in widgets)
        return translator("maintenance_interface_ok", titles=titles)

    def _schedule_background_tasks(self) -> str:
        app_count = len(list(self.os_reference.application_manager.list_applications()))
        translator = self.os_reference.language_manager.translate
        return translator("maintenance_background", count=app_count)


__all__ = ["FileIntegrityVerifier", "AutoMaintenanceGuardian"]
