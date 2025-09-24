"""High-level integration of Mini OS components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from .applications import ApplicationManager, DEFAULT_APPLICATIONS
from .interfaces import InterfaceManager, Widget
from .localization import LanguageManager
from .maintenance import AutoMaintenanceGuardian, FileIntegrityVerifier


@dataclass
class MiniOS:
    """Represents the running Mini OS environment."""

    language_manager: LanguageManager | None = None
    interface_manager: InterfaceManager | None = None
    application_manager: ApplicationManager = field(default_factory=ApplicationManager)
    integrity_verifier: FileIntegrityVerifier | None = None
    maintenance_guardian: AutoMaintenanceGuardian = field(init=False)

    def __post_init__(self) -> None:
        lang_manager: LanguageManager
        if self.language_manager is None:
            lang_manager, _ = LanguageManager.load_or_initialize()
            self.language_manager = lang_manager
        else:
            lang_manager = self.language_manager

        if self.interface_manager is None:
            self.interface_manager = InterfaceManager(translator=lang_manager.translate)
        else:
            self.interface_manager.set_translator(lang_manager.translate)

        if self.integrity_verifier is None:
            self.integrity_verifier = FileIntegrityVerifier.default_manifest(
                language_manager=lang_manager
            )

        for app in DEFAULT_APPLICATIONS:
            self.application_manager.install(app)
        translator = self.language_manager.translate
        self.interface_manager.register_widget(
            Widget(
                title=translator("welcome_widget_title"),
                icon="✨",
                body=translator("welcome_widget_body"),
            )
        )
        self.interface_manager.register_widget(
            Widget(
                title=translator("snapshot_widget_title"),
                icon="🛡️",
                body=translator("snapshot_widget_body"),
            )
        )
        self.interface_manager.register_widget(
            Widget(
                title=translator("quick_widget_title"),
                icon="🎛️",
                body=translator("quick_widget_body"),
            )
        )
        self.maintenance_guardian = AutoMaintenanceGuardian(self)

    def list_app_names(self) -> List[str]:
        return [app.name for app in self.application_manager.list_applications()]

    def open_application(self, name: str) -> str:
        return self.application_manager.launch(name)

    def render_home(self) -> str:
        return self.interface_manager.render_home()

    def render_app_menu(self) -> str:
        return self.interface_manager.render_app_menu(self.list_app_names())

    def render_desktop(self) -> str:
        return self.interface_manager.render_desktop(self.list_app_names())

    def render_start_menu(self) -> str:
        return self.interface_manager.render_start_menu(self.list_app_names())

    def render_boot_splash(self, steps: Sequence[str]) -> str:
        title = self.language_manager.translate("boot_title")
        return self.interface_manager.render_boot_splash(title, steps)

    def describe(self) -> str:
        return self.language_manager.translate("describe_text")

    def run_auto_maintenance(self) -> List[str]:
        return self.maintenance_guardian.run_startup_jobs()
