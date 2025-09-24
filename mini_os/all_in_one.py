"""High-level integration of Mini OS components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .applications import ApplicationManager, DEFAULT_APPLICATIONS
from .interfaces import InterfaceManager, Widget
from .maintenance import AutoMaintenanceGuardian, FileIntegrityVerifier
from .security import AntivirusEngine, SandboxManager, VirtualStorageManager


@dataclass
class MiniOS:
    """Represents the running Mini OS environment."""

    interface_manager: InterfaceManager = field(default_factory=InterfaceManager)
    application_manager: ApplicationManager = field(default_factory=ApplicationManager)
    integrity_verifier: FileIntegrityVerifier = field(
        default_factory=FileIntegrityVerifier.default_manifest
    )
    maintenance_guardian: AutoMaintenanceGuardian = field(init=False)
    antivirus: AntivirusEngine = field(init=False)
    sandbox_manager: SandboxManager = field(default_factory=SandboxManager)
    storage_manager: VirtualStorageManager = field(default_factory=VirtualStorageManager)

    def __post_init__(self) -> None:
        for app in DEFAULT_APPLICATIONS:
            self.application_manager.install(app)
        self.interface_manager.register_widget(
            Widget(
                title="Welcome to MiniOS",
                body=(
                    "Use the application menu to explore built-in apps.\n"
                    "This is a toy example showing how components can be separated."
                ),
            )
        )
        self.maintenance_guardian = AutoMaintenanceGuardian(self)
        self.antivirus = AntivirusEngine(self.integrity_verifier)
        self._provision_security_baseline()

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

    def run_security_suite(self) -> List[str]:
        """Execute antivirus, sandbox, and storage reporting."""

        observations = self.antivirus.scan()
        security_log = [self.antivirus.summarize(observations)]
        security_log.append(self.sandbox_manager.describe())
        security_log.append(self.storage_manager.describe())
        return security_log

    # Internal helpers -------------------------------------------------

    def _provision_security_baseline(self) -> None:
        """Seed sandbox policies and virtual storage defaults."""

        # System volume holds shared assets. Individual application homes are
        # nested beneath for easy discovery.
        system_volume = self.storage_manager.ensure_volume("system", quota_bytes=5 * 1024 * 1024)
        apps_volume = self.storage_manager.ensure_volume("apps", quota_bytes=2 * 1024 * 1024)

        self.storage_manager.write_text(
            "system",
            "README.txt",
            (
                "Ragnar MiniOS virtual storage\n"
                "-----------------------------\n"
                "System artifacts and configuration snippets live here."
            ),
        )

        for app in self.application_manager.list_applications():
            app_home = apps_volume.root / app.name.lower().replace(" ", "_")
            app_home.mkdir(parents=True, exist_ok=True)
            self.sandbox_manager.ensure_policy(app.name, [app_home, system_volume.root])
            placeholder = app_home / "profile.json"
            if not placeholder.exists():
                placeholder.write_text("{}\n")
