"""User interface utilities for the Ragnar Mini OS."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from itertools import zip_longest
from typing import Iterable, List, Sequence, Tuple


RESET = "\033[0m"

_ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


# Shared icon map so both the textual and graphical shells can keep a
# consistent visual language.
APP_ICON_MAP: dict[str, str] = {
    "Notes": "📝",
    "Terminal": "💻",
    "Settings": "⚙️",
    "Calculator": "🧮",
    "Weather": "☀️",
    "Calendar": "📅",
    "Music": "🎶",
    "News": "📰",
    "System Monitor": "📊",
}


def resolve_app_icon(app_name: str) -> str:
    """Return a decorative icon for the given application."""

    return APP_ICON_MAP.get(app_name, "🪟")


def _visible_length(text: str) -> int:
    """Return the display length of a string ignoring ANSI escape codes."""

    return len(_ANSI_PATTERN.sub("", text))


def _pad_visible(text: str, width: int) -> str:
    """Pad a possibly colourised string so its visible width matches ``width``."""

    visible = _visible_length(text)
    if visible >= width:
        return text
    return text + " " * (width - visible)


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

    # ------------------------------------------------------------------
    # Desktop & start menu renderers

    def render_desktop(self, app_names: Sequence[str]) -> str:
        """Render a faux desktop showing applications as neon icons."""

        if not app_names:
            return self.theme.render_empty_state()

        header = self.theme.render_tagline("Neon Desktop")
        columns = 3
        padded_names = list(app_names)
        rows: List[str] = []
        grouped = zip_longest(*(padded_names[i::columns] for i in range(columns)), fillvalue="")
        for group in grouped:
            cells: List[str] = []
            for name in group:
                if not name:
                    cells.append(" " * 20)
                    continue
                icon = resolve_app_icon(name)
                label = f"{icon}  {name}"
                cells.append(self.theme.secondary(f"{label:<20}"))
            rows.append("  ".join(cells).rstrip())

        panel_width = max(_visible_length(row) for row in rows) if rows else 0
        top = self.theme.accent("╔" + "═" * (panel_width + 2) + "╗")
        bottom = self.theme.accent("╚" + "═" * (panel_width + 2) + "╝")
        body = [
            self.theme.accent("║ ")
            + _pad_visible(row, panel_width)
            + self.theme.accent(" ║")
            for row in rows
        ]
        layout = "\n".join([top, *body, bottom])

        bar_content = "⊞ Start  ⌕ Search  ☰ Widgets  🔔 Focus  12:00"
        padded_bar = f"{bar_content:<{panel_width + 2}}"
        taskbar_lines = [
            self.theme.accent("┏" + "━" * (panel_width + 2) + "┓"),
            self.theme.primary(f"┃ {padded_bar} ┃"),
            self.theme.accent("┗" + "━" * (panel_width + 2) + "┛"),
        ]
        taskbar = "\n".join(taskbar_lines)

        return "\n".join([header, layout, taskbar])

    def render_start_menu(self, app_names: Sequence[str]) -> str:
        """Render a Start menu style launcher panel."""

        header = self.theme.render_tagline("Start Menu")
        pinned = list(app_names[:6])
        pinned_lines = [self.theme.accent("Pinned")]
        if not pinned:
            pinned_lines.append(self.theme.secondary("  (nothing pinned yet)"))
        else:
            for name in pinned:
                icon = resolve_app_icon(name)
                pinned_lines.append(
                    f"  {self.theme.primary(icon)} {self.theme.secondary(name)}"
                )

        all_apps_header = self.theme.accent("All Apps")
        menu_entries = []
        for index, name in enumerate(app_names, start=1):
            badge = self.theme.surface(f"{index:02d}")
            menu_entries.append(f"  {badge} {self.theme.secondary(name)}")
        if not menu_entries:
            menu_entries.append(self.theme.secondary("  (no applications installed)"))

        panel = [header, "\n".join(pinned_lines), all_apps_header, "\n".join(menu_entries)]
        return "\n\n".join(panel)

    def render_boot_splash(self, title: str, steps: Sequence[str]) -> str:
        """Render a luminous boot splash screen with a progress pulse."""

        logo_raw = [
            "      ██████╗  █████╗  ██████╗  ███╗   ██╗",
            "     ██╔════╝ ██╔══██╗██╔═══██╗ ████╗  ██║",
            "     ██║  ███╗███████║██║   ██║ ██╔██╗ ██║",
            "     ██║   ██║██╔══██║██║   ██║ ██║╚██╗██║",
            "     ╚██████╔╝██║  ██║╚██████╔╝ ██║ ╚████║",
            "      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═╝  ╚═══╝",
        ]

        subtitle = self.theme.secondary("Booting Ragnar MiniOS · ultra neon edition")

        total = max(len(steps), 1)
        orbit_symbols = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        stage_lines = []
        for index, step in enumerate(steps, start=1):
            pulse = orbit_symbols[index % len(orbit_symbols)]
            stage_lines.append(
                f" {self.theme.accent(pulse)} {self.theme.secondary(step)}"
            )

        progress_ratio = len(steps) / total
        segments = 20
        filled_segments = max(1, int(progress_ratio * segments))
        bar = (
            self.theme.accent("▰" * filled_segments)
            + self.theme.secondary("▱" * (segments - filled_segments))
        )
        progress_label = self.theme.primary(f"Loading modules {len(steps):02d}/{total:02d}")
        progress_text = f"{bar} {progress_label}"

        stage_preview = stage_lines[-4:]
        content_candidates = [
            max(len(line) for line in logo_raw),
            _visible_length(subtitle),
            _visible_length(progress_text),
        ]
        content_candidates.extend(_visible_length(line) for line in stage_preview)
        content_width = max(content_candidates)
        frame_width = max(58, content_width + 2)
        border_top = self.theme.accent("╔" + "═" * frame_width + "╗")
        border_bottom = self.theme.accent("╚" + "═" * frame_width + "╝")

        padded_logo = [
            f"║ {_pad_visible(self.theme.primary(line), frame_width - 2)} ║"
            for line in logo_raw
        ]
        blank_line = f"║ {'':<{frame_width - 2}} ║"
        subtitle_line = f"║ {_pad_visible(subtitle, frame_width - 2)} ║"
        progress_line = f"║ {_pad_visible(progress_text, frame_width - 2)} ║"
        stage_block = [
            f"║ {_pad_visible(line, frame_width - 2)} ║"
            for line in stage_preview
        ]
        while len(stage_block) < 4:
            stage_block.insert(0, blank_line)

        splash_lines = [
            border_top,
            *padded_logo,
            blank_line,
            subtitle_line,
            blank_line,
            *stage_block,
            blank_line,
            progress_line,
            blank_line,
            border_bottom,
        ]
        title_line = self.theme.render_tagline(title)
        return "\n".join([title_line, *splash_lines])
