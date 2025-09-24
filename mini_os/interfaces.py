"""User interface utilities for the Ragnar Mini OS."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


RESET = "\033[0m"


@dataclass
class Theme:
    """Styling helpers used to render vibrant console interfaces."""

    name: str
    accent_color: str
    primary_color: str
    secondary_color: str
    surface_color: str
    banner_lines: Sequence[Tuple[str, str]]
    enable_color: bool = True

    @classmethod
    def neon(cls, enable_color: bool = True) -> "Theme":
        """Return a colourful neon inspired theme."""

        banner = (
            ("\033[38;2;0;255;255m", "╔╦╗╦╔╗╔╦╔═╗╦ ╦   ╔╦╗╔═╗"),
            ("\033[38;2;111;0;255m", " ║ ║║║║║╠═╣║ ║─── ║║ ║╣ "),
            ("\033[38;2;255;0;128m", " ╩ ╩╝╚╝╩╩ ╩╚═╝   ═╩╝╚═╝"),
        )
        return cls(
            name="Neon Horizon",
            accent_color="\033[38;2;255;0;170m",
            primary_color="\033[38;2;204;255;255m",
            secondary_color="\033[38;2;173;196;255m",
            surface_color="\033[38;2;144;238;144m",
            banner_lines=banner,
            enable_color=enable_color,
        )

    def _apply(self, color: str, text: str) -> str:
        if not self.enable_color:
            return text
        return f"{color}{text}{RESET}"

    def accent(self, text: str) -> str:
        return self._apply(self.accent_color, text)

    def primary(self, text: str) -> str:
        return self._apply(self.primary_color, text)

    def secondary(self, text: str) -> str:
        return self._apply(self.secondary_color, text)

    def surface(self, text: str) -> str:
        return self._apply(self.surface_color, text)

    def render_banner(self) -> str:
        return "\n".join(self._apply(color, line) for color, line in self.banner_lines)

    def render_tagline(self, text: str) -> str:
        bar = self.accent("━" * len(text))
        return f"{self.primary(text)}\n{bar}"

    def render_status(self, widget_count: int) -> str:
        jewel = self.accent("◆")
        descriptor = f"{widget_count} widget{'s' if widget_count != 1 else ''} ready"
        return self.secondary(f"{jewel} {descriptor} · Theme: {self.name}")

    def render_empty_state(self) -> str:
        return self.secondary("No widgets registered yet. Add one to light up the desktop.")

    def divider(self, width: int) -> str:
        return self.accent("─" * width)


@dataclass
class Widget:
    """A tiny data structure representing a UI widget on the screen."""

    title: str
    body: str
    icon: str | None = None

    def render(self, theme: Theme) -> str:
        """Render the widget inside a decorative neon panel."""

        decorated_title = f"{self.icon}  {self.title}" if self.icon else self.title
        body_lines = self.body.splitlines() or [""]
        content_width = max(len(decorated_title), *(len(line) for line in body_lines))
        border_width = content_width + 2
        top = theme.accent("╭" + "─" * border_width + "╮")
        bottom = theme.accent("╰" + "─" * border_width + "╯")
        header = theme.accent("│") + theme.primary(f" {decorated_title:^{content_width}} ") + theme.accent("│")
        separator = theme.accent("├" + "─" * border_width + "┤")

        rows = [
            theme.accent("│")
            + theme.secondary(f" {line:<{content_width}} ")
            + theme.accent("│")
            for line in body_lines
        ]
        widget_lines = [top, header, separator, *rows, bottom]
        return "\n".join(widget_lines)


class InterfaceManager:
    """Responsible for rendering different textual interfaces of the Mini OS."""

    def __init__(self, theme: Theme | None = None, enable_color: bool | None = None) -> None:
        if enable_color is None:
            disable_color = os.environ.get("MINIOS_NO_COLOR", "").lower() in {"1", "true", "yes"}
            enable_color = not disable_color
        self.theme: Theme = theme or Theme.neon(enable_color=enable_color)
        self.widgets: List[Widget] = []

    def set_theme(self, theme: Theme) -> None:
        """Update the active theme used when rendering the UI."""

        self.theme = theme

    def register_widget(self, widget: Widget) -> None:
        """Add a widget that will be displayed on the home interface."""

        self.widgets.append(widget)

    def render_home(self) -> str:
        """Render the home interface, showing all registered widgets."""

        parts: List[str] = [self.theme.render_banner(), self.theme.render_tagline("Welcome back to MiniOS")]
        if not self.widgets:
            parts.append(self.theme.render_empty_state())
        else:
            rendered = [widget.render(self.theme) for widget in self.widgets]
            parts.append("\n\n".join(rendered))
        parts.append(self.theme.render_status(len(self.widgets)))
        return "\n\n".join(parts)

    def render_app_menu(self, app_names: Iterable[str]) -> str:
        """Render a neon-styled textual app menu."""

        menu_lines = [self.theme.render_tagline("Available Applications")]
        for index, name in enumerate(app_names, start=1):
            badge = self.theme.surface(f"{index:02d}")
            menu_lines.append(f"  {badge} {self.theme.secondary(name)}")
        if len(menu_lines) == 1:
            menu_lines.append(self.theme.secondary("  (no applications installed)"))
        return "\n".join(menu_lines)
