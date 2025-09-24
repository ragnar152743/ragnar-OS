"""Application management for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import math
import os
import random
from textwrap import dedent
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
    today = date.today().strftime("%Y-%m-%d")
    template = dedent(
        f"""
        Notes App
        ---------
        Today is {today}.
        • Tip: Capture ideas quickly so they do not slip away.
        • You can extend this prototype to persist notes to disk.
        """
    ).strip()
    return template


def _terminal_app() -> str:
    commands = [
        "$ whoami",
        os.getenv("USER", "mini"),
        "$ pwd",
        os.getcwd(),
        "$ ls",
        "  " + "\n  ".join(sorted(os.listdir("."))),
    ]
    body = "\n".join(commands)
    return f"Terminal App\n------------\n{body}"


def _settings_app() -> str:
    body = dedent(
        """
        Settings App
        ------------
        Appearance : Light
        Connectivity: Online (simulated)
        Updates     : Automatic via the Maintenance Guardian
        """
    ).strip()
    return body


def _calculator_app() -> str:
    operations = {
        "42 × 13": 42 * 13,
        "255 ÷ 3": 255 / 3,
        "√256": math.isqrt(256),
        "sin(π / 6)": round(math.sin(math.pi / 6), 2),
    }
    lines = ["Calculator App", "--------------"]
    lines.extend(f"{expr} = {value}" for expr, value in operations.items())
    return "\n".join(lines)


def _weather_app() -> str:
    forecasts = [
        "Sunny with a gentle breeze",
        "Cloudy morning turning into clear skies",
        "Light showers expected in the afternoon",
        "Thunderstorms building over the evening",
    ]
    random.seed(date.today().toordinal())
    forecast = random.choice(forecasts)
    temperature = 18 + random.randint(-3, 5)
    return dedent(
        f"""
        Weather Center
        --------------
        Location : Local Simulated Node
        Forecast : {forecast}
        Temperature: {temperature}°C
        """
    ).strip()


def _calendar_app() -> str:
    import calendar

    now = datetime.now()
    month_view = calendar.TextCalendar().formatmonth(now.year, now.month).rstrip()
    lines = ["Calendar Hub", "------------", month_view]
    return "\n".join(lines)


def _music_app() -> str:
    playlist = [
        ("Sunrise Echoes", "L. Vega", 3.42),
        ("Nebula Drift", "Q. Harper", 4.05),
        ("Velvet Circuit", "K. Ito", 5.11),
    ]
    lines = ["HoloMusic Player", "-----------------", "Current Playlist:"]
    for title, artist, length in playlist:
        lines.append(f" • {title} — {artist} ({length:.2f} min)")
    lines.append("Tip: Integrate with an audio backend to stream real tracks!")
    return "\n".join(lines)


def _news_app() -> str:
    headlines = [
        "MiniOS gains automatic maintenance guardian",
        "Developers celebrate reliable integrity checks",
        "Textual interfaces remain delightfully hackable",
    ]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["Daily Brief", "-----------", f"Updated: {now}"]
    lines.extend(f" • {headline}" for headline in headlines)
    return "\n".join(lines)


def _system_monitor_app() -> str:
    uptime_seconds = datetime.now().timestamp() - pseudo_boot_timestamp()
    load_avg = get_load_average()
    lines = ["System Monitor", "--------------"]
    lines.append(f"Uptime (simulated): {uptime_seconds:.0f} seconds")
    lines.append(f"Load average (1/5/15 min): {load_avg}")
    lines.append("Processes observed: Stable and responsive")
    return "\n".join(lines)


_BOOT_TIMESTAMP: Optional[float] = None


def pseudo_boot_timestamp() -> float:
    """Return a lazily initialised timestamp marking the module import time."""

    global _BOOT_TIMESTAMP
    if _BOOT_TIMESTAMP is None:
        _BOOT_TIMESTAMP = datetime.now().timestamp()
    return _BOOT_TIMESTAMP


def get_load_average() -> str:
    """Return a platform friendly load average string."""

    try:
        load1, load5, load15 = os.getloadavg()
        return f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
    except (AttributeError, OSError):
        return "n/a"


DEFAULT_APPLICATIONS = [
    Application("Notes", "Take quick notes.", _notes_app),
    Application("Terminal", "Run shell-like commands.", _terminal_app),
    Application("Settings", "Adjust system preferences.", _settings_app),
    Application("Calculator", "Perform handy math operations.", _calculator_app),
    Application("Weather", "Get the latest simulated forecast.", _weather_app),
    Application("Calendar", "Check your current monthly schedule.", _calendar_app),
    Application("Music", "Browse the holographic playlist.", _music_app),
    Application("News", "Read fresh simulated headlines.", _news_app),
    Application("System Monitor", "Inspect runtime stats.", _system_monitor_app),
]
