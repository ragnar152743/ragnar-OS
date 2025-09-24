"""Application management for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from statistics import mean
from typing import Callable, Dict, Iterable, Optional

from .utils import format_table


@dataclass
class Application:
    """Simple representation of an application within the Mini OS."""

    name: str
    description: str
    entrypoint: Callable[[], str]
    version: str = "1.0.0"

    def run(self) -> str:
        return self.entrypoint()


class ApplicationManager:
    """Responsible for installing, listing, and launching applications."""

    def __init__(self) -> None:
        self._applications: Dict[str, Application] = {}

    def install(self, app: Application, *, overwrite: bool = False) -> bool:
        """Install or update an application.

        Returns ``True`` if the application was installed or updated, and
        ``False`` when the request was ignored (e.g. attempting to install an
        older version over a newer one).
        """

        existing = self._applications.get(app.name)
        if existing is None or overwrite:
            self._applications[app.name] = app
            return True

        if compare_versions(app.version, existing.version) > 0:
            self._applications[app.name] = app
            return True

        return False

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


def compare_versions(left: str, right: str) -> int:
    """Return -1, 0, or 1 comparing dotted version strings."""

    def split(version: str) -> tuple[int, ...]:
        return tuple(int(part) for part in version.split("."))

    left_parts = split(left)
    right_parts = split(right)
    length = max(len(left_parts), len(right_parts))
    padded_left = left_parts + (0,) * (length - len(left_parts))
    padded_right = right_parts + (0,) * (length - len(right_parts))

    if padded_left < padded_right:
        return -1
    if padded_left > padded_right:
        return 1
    return 0


# Predefined applications -------------------------------------------------

def _notes_app() -> str:
    today = date.today().strftime("%Y-%m-%d")
    return (
        "Notes\n"
        "-----\n"
        f"[{today}] Buy milk, schedule stand-up, update Ragnar OS roadmap.\n"
        "Tip: sync with the cloud to share notes across devices."
    )


def _terminal_app() -> str:
    commands = [
        "$ whoami",
        "mini-user",
        "$ uptime",
        "up 3 days, 04:12",
        "$ ls apps",
        "calculator  journal  media  system-monitor",
    ]
    return "Terminal\n--------\n" + "\n".join(commands)


def _settings_app() -> str:
    options = {
        "Wi-Fi": "Connected",
        "Bluetooth": "Enabled",
        "Theme": "Nordic Night",
        "Automatic updates": "Active",
    }
    return "Settings\n--------\n" + format_table(options.items())


def _calculator_app() -> str:
    expression = "((42 / 6) + 7) * 3"
    result = ((42 / 6) + 7) * 3
    return (
        "Calculator\n-----------\n"
        f"Expression: {expression}\n"
        f"Result: {result:g}\n"
        "Functions available: add, subtract, multiply, divide."
    )


def _weather_app() -> str:
    city = "Reykjavík"
    forecast = [
        ("Today", "5°C", "Partly cloudy"),
        ("Tomorrow", "7°C", "Light rain"),
        ("In 2 days", "6°C", "Overcast"),
    ]
    rows = [" | ".join(row) for row in forecast]
    return (
        "Weather\n-------\n"
        f"City: {city}\n"
        + "\n".join(rows)
        + "\nData source: MiniOS meteorological service (simulated)."
    )


def _news_app() -> str:
    headlines = [
        "MiniOS introduces an autonomous update system.",
        "Developers celebrate increased modularity in Ragnar OS.",
        "Security team reports zero compromised files after new checks.",
    ]
    return "Newsroom\n--------\n" + "\n".join(f"- {headline}" for headline in headlines)


def _journal_app() -> str:
    entries = [
        ("Morning", "Reviewed build pipeline, scheduled health check."),
        ("Afternoon", "Implemented automatic updates."),
        ("Evening", "Verified integrity checks for deployment."),
    ]
    formatted = "\n".join(f"{slot}: {text}" for slot, text in entries)
    return "Journal\n-------\n" + formatted


def _system_monitor_app() -> str:
    processes = [
        ("init", 1, 0.1),
        ("update-manager", 32, 0.3),
        ("app-store", 48, 1.7),
        ("ui", 64, 0.5),
    ]
    average_cpu = mean(cpu for _, _, cpu in processes)
    lines = [
        "System Monitor\n--------------",
        format_table((proc, f"PID {pid}", f"CPU {cpu:.1f}%") for proc, pid, cpu in processes),
        f"Average CPU load: {average_cpu:.1f}%",
    ]
    return "\n".join(lines)


def _media_app() -> str:
    playlist = [
        ("Aurora", "Northern Lights"),
        ("Valhalla", "Legends Awake"),
        ("Skald", "Ballad of the North"),
    ]
    timestamp = datetime.now().strftime("%H:%M:%S")
    lines = ["Media Player\n------------", f"Playlist loaded at {timestamp}"]
    lines.extend(f"* {artist} – {title}" for artist, title in playlist)
    return "\n".join(lines)


DEFAULT_APPLICATIONS = [
    Application("Notes", "Take quick notes.", _notes_app, version="1.1.0"),
    Application("Terminal", "Run shell-like commands.", _terminal_app, version="1.2.0"),
    Application("Settings", "Adjust system preferences.", _settings_app, version="1.1.0"),
    Application("Calculator", "Solve quick maths.", _calculator_app, version="1.0.0"),
    Application("Weather", "Check the weather outlook.", _weather_app, version="1.0.0"),
    Application("Newsroom", "Read curated tech headlines.", _news_app, version="1.0.0"),
    Application("Journal", "Track the day's achievements.", _journal_app, version="1.0.0"),
    Application("System Monitor", "Inspect key processes.", _system_monitor_app, version="1.0.0"),
    Application("Media Player", "Play your favourite tunes.", _media_app, version="1.0.0"),
]
