"""High-level integration of Mini OS components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .applications import ApplicationManager, DEFAULT_APPLICATIONS
from .interfaces import InterfaceManager, Widget


@dataclass
class MiniOS:
    """Represents the running Mini OS environment."""

    interface_manager: InterfaceManager = field(default_factory=InterfaceManager)
    application_manager: ApplicationManager = field(default_factory=ApplicationManager)

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
