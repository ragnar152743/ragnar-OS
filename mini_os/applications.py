"""Application management for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional


@dataclass
class Application:
    """Simple representation of an application within the Mini OS."""

    name: str
    description: str
    entrypoint: Callable[[], str]

    def run(self) -> str:
        return self.entrypoint()


class ApplicationManager:
    """Responsible for installing, listing, and launching applications."""

    def __init__(self) -> None:
        self._applications: Dict[str, Application] = {}

    def install(self, app: Application) -> None:
        self._applications[app.name] = app

    def uninstall(self, name: str) -> bool:
        return self._applications.pop(name, None) is not None

    def list_applications(self) -> Iterable[Application]:
        return self._applications.values()

    def get(self, name: str) -> Optional[Application]:
        return self._applications.get(name)

    def launch(self, name: str) -> str:
        app = self.get(name)
        if app is None:
            raise KeyError(f"No application named {name!r} is installed.")
        return app.run()


# Predefined applications -------------------------------------------------

def _notes_app() -> str:
    return "Notes App\n---------\nNothing to see here yet, but you can jot down your ideas!"


def _terminal_app() -> str:
    return "Terminal App\n------------\n$ echo 'Hello from MiniOS'\nHello from MiniOS"


def _settings_app() -> str:
    return "Settings App\n------------\n(Imagine configuration toggles living here.)"


DEFAULT_APPLICATIONS = [
    Application("Notes", "Take quick notes.", _notes_app),
    Application("Terminal", "Run shell-like commands.", _terminal_app),
    Application("Settings", "Adjust system preferences.", _settings_app),
]
