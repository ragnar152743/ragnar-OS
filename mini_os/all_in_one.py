"""High-level integration of Mini OS components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .applications import ApplicationManager, DEFAULT_APPLICATIONS
from .interfaces import InterfaceManager, Widget
from .maintenance import AutoMaintenanceGuardian, FileIntegrityVerifier


@dataclass
class MiniOS:
    """Represents the running Mini OS environment."""

    interface_manager: InterfaceManager = field(default_factory=InterfaceManager)
    application_manager: ApplicationManager = field(default_factory=ApplicationManager)
    integrity_verifier: FileIntegrityVerifier = field(
        default_factory=FileIntegrityVerifier.default_manifest
    )
    maintenance_guardian: AutoMaintenanceGuardian = field(init=False)

    def __post_init__(self) -> None:
        for app in DEFAULT_APPLICATIONS:
            self.application_manager.install(app)
        self.interface_manager.register_widget(
            Widget(
                title="Welcome to MiniOS",
                icon="✨",
                body=(
                    "Use the application menu to explore built-in apps.\n"
                    "This is a toy example showing how components can be separated."
                ),
            )
        )
        self.interface_manager.register_widget(
            Widget(
                title="System Snapshot",
                icon="🛡️",
                body=(
                    "Integrity status: PASS\n"
                    "Maintenance queue: All background jobs scheduled"
                ),
            )
        )
        self.interface_manager.register_widget(
            Widget(
                title="Quick Actions",
                icon="🎛️",
                body=(
                    "F1  View app marketplace preview\n"
                    "F2  Inspect service registry\n"
                    "F3  Launch the system monitor"
                ),
            )
        )
        self.maintenance_guardian = AutoMaintenanceGuardian(self)

    def list_app_names(self) -> Iterable[str]:
        return (app.name for app in self.application_manager.list_applications())

    def open_application(self, name: str) -> str:
        return self.application_manager.launch(name)

    def render_home(self) -> str:
        return self.interface_manager.render_home()

    def render_app_menu(self) -> str:
        return self.interface_manager.render_app_menu(self.list_app_names())

    def describe(self) -> str:
        return (
            "MiniOS integrates dedicated components: one for interfaces, "
            "another for applications, a boot sequence in Python, and a "
            "controller that ties everything together."
        )

    def run_auto_maintenance(self) -> List[str]:
        return self.maintenance_guardian.run_startup_jobs()
