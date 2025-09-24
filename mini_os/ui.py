"""Desktop shell abstractions for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .interfaces import Widget


@dataclass
class Theme:
    name: str
    stylesheet: str


class ThemeManager:
    def __init__(self) -> None:
        self._themes: Dict[str, Theme] = {
            "hacker": Theme("hacker", "background: #000; color: #0f0;"),
            "minimal": Theme("minimal", "background: #fff; color: #111;"),
            "neon": Theme("neon", "background: #111; color: #f0f;"),
        }
        self._current = self._themes["minimal"]

    def set_theme(self, name: str) -> Theme:
        self._current = self._themes[name]
        return self._current

    def current(self) -> Theme:
        return self._current


@dataclass
class Notification:
    title: str
    body: str


class NotificationCenter:
    def __init__(self) -> None:
        self._notifications: List[Notification] = []
        self._dnd = False

    def push(self, title: str, body: str) -> None:
        if not self._dnd:
            self._notifications.append(Notification(title, body))

    def enable_dnd(self, enabled: bool) -> None:
        self._dnd = enabled

    def list(self) -> List[Notification]:
        return list(self._notifications)


class Launcher:
    """Fuzzy search launcher."""

    def __init__(self) -> None:
        self._entries: Dict[str, str] = {}

    def register(self, name: str, description: str) -> None:
        self._entries[name] = description

    def search(self, query: str) -> List[str]:
        query = query.lower()
        return [name for name in self._entries if query in name.lower()]


@dataclass
class ControlToggle:
    name: str
    state: bool


class ControlCenter:
    def __init__(self) -> None:
        self._toggles: Dict[str, ControlToggle] = {
            "network": ControlToggle("network", True),
            "themes": ControlToggle("themes", True),
            "sessions": ControlToggle("sessions", True),
        }

    def set_toggle(self, name: str, state: bool) -> None:
        if name in self._toggles:
            self._toggles[name].state = state

    def snapshot(self) -> Dict[str, bool]:
        return {name: toggle.state for name, toggle in self._toggles.items()}


@dataclass
class DesktopShell:
    """High level UI front-end description."""

    launcher: Launcher = field(default_factory=Launcher)
    control_center: ControlCenter = field(default_factory=ControlCenter)
    notification_center: NotificationCenter = field(default_factory=NotificationCenter)
    theme_manager: ThemeManager = field(default_factory=ThemeManager)
    widgets: List[Widget] = field(default_factory=list)

    def register_widget(self, widget: Widget) -> None:
        self.widgets.append(widget)

    def render(self) -> str:
        theme = self.theme_manager.current()
        sections = [f"Desktop Theme: {theme.name}"]
        sections.extend(widget.render() for widget in self.widgets)
        return "\n".join(sections)
