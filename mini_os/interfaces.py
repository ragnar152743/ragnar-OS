"""User interface utilities for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Widget:
    """A tiny data structure representing a UI widget on the screen."""

    title: str
    body: str

    def render(self) -> str:
        border = "=" * len(self.title)
        return f"{self.title}\n{border}\n{self.body}\n"


class InterfaceManager:
    """Responsible for rendering different textual interfaces of the Mini OS."""

    def __init__(self) -> None:
        self.widgets: List[Widget] = []

    def register_widget(self, widget: Widget) -> None:
        """Add a widget that will be displayed on the home interface."""

        self.widgets.append(widget)

    def render_home(self) -> str:
        """Render the home interface, showing all registered widgets."""

        if not self.widgets:
            return "MiniOS Home\n==========\nNo widgets registered yet.\n"
        rendered = [widget.render() for widget in self.widgets]
        return "\n".join(rendered)

    def render_app_menu(self, app_names: Iterable[str]) -> str:
        """Render a simple textual app menu."""

        menu_lines = ["Available Applications:"]
        for index, name in enumerate(app_names, start=1):
            menu_lines.append(f"  {index}. {name}")
        if len(menu_lines) == 1:
            menu_lines.append("  (no applications installed)")
        return "\n".join(menu_lines)
