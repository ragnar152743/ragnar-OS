"""Automatic update utilities for MiniOS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .applications import Application, ApplicationManager, DEFAULT_APPLICATIONS, compare_versions


@dataclass
class UpdateSummary:
    """Result of an update operation."""

    checked: List[str]
    updated: List[str]

    def render(self) -> str:
        lines = ["Update summary:"]
        for app in self.checked:
            lines.append(f" - {app}")
        if self.updated:
            lines.append("Updated applications:")
            lines.extend(f" * {app}" for app in self.updated)
        else:
            lines.append("No updates were necessary.")
        return "\n".join(lines)


class UpdateManager:
    """Simple automatic update manager using a local catalog."""

    def __init__(self, application_manager: ApplicationManager, catalog: Iterable[Application] | None = None) -> None:
        self.application_manager = application_manager
        self.catalog: Dict[str, Application] = {
            app.name: app for app in (catalog or DEFAULT_APPLICATIONS)
        }

    def check_for_updates(self) -> list[str]:
        """Return a description of pending updates."""

        pending: list[str] = []
        for name, catalog_app in self.catalog.items():
            installed = self.application_manager.get(name)
            if installed is None:
                pending.append(f"{name}: not installed")
            elif compare_versions(installed.version, catalog_app.version) < 0:
                pending.append(
                    f"{name}: {installed.version} -> {catalog_app.version}"
                )
        return pending

    def apply_updates(self) -> list[str]:
        """Install any missing apps or upgrades from the catalog."""

        updated: list[str] = []
        for name, catalog_app in self.catalog.items():
            installed = self.application_manager.get(name)
            if installed is None or compare_versions(installed.version, catalog_app.version) < 0:
                self.application_manager.install(catalog_app, overwrite=True)
                updated.append(name)
        return updated

    def run(self) -> UpdateSummary:
        checked = self.check_for_updates()
        applied = self.apply_updates()
        return UpdateSummary(checked=checked, updated=applied)

