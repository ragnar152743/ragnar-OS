"""Advanced application management for Ragnar Mini OS."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date, datetime
import math
import os
import random
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, Iterable, List, Optional

from .kernel import SandboxManager, SandboxPolicy


@dataclass
class AppManifest:
    name: str
    version: str
    description: str
    permissions: Dict[str, bool]
    icon: str
    hooks: Dict[str, str]


@dataclass
class LifecycleHooks:
    on_install: Optional[Callable[[AppManifest], str]] = None
    on_update: Optional[Callable[[AppManifest], str]] = None
    on_uninstall: Optional[Callable[[AppManifest], str]] = None


@dataclass
class ApplicationPackage:
    manifest: AppManifest
    entrypoint: Callable[[], str]
    hooks: LifecycleHooks = field(default_factory=LifecycleHooks)

    def execute(self) -> str:
        return self.entrypoint()


@dataclass
class Application:
    package: ApplicationPackage
    sandbox_policy: SandboxPolicy

    @property
    def name(self) -> str:
        return self.package.manifest.name

    def run(self) -> str:
        return self.package.execute()


class ApplicationWatcher:
    """Simulated hot reload watcher using asyncio tasks."""

    def __init__(self) -> None:
        self._listeners: Dict[str, Callable[[], None]] = {}

    def watch(self, app: str, callback: Callable[[], None]) -> None:
        self._listeners[app] = callback

    async def trigger(self, app: str) -> None:
        if app in self._listeners:
            await asyncio.sleep(0)
            self._listeners[app]()


class ApplicationManager:
    """Handles installation, lifecycle, and execution of applications."""

    def __init__(self, sandbox_manager: SandboxManager) -> None:
        self._sandbox_manager = sandbox_manager
        self._applications: Dict[str, Application] = {}
        self._watcher = ApplicationWatcher()

    def install(self, package: ApplicationPackage) -> str:
        policy = SandboxPolicy(allowed_paths=("/",), network=package.manifest.permissions.get("network", False))
        sandbox = self._sandbox_manager.create(package.manifest.name, policy)
        app = Application(package=package, sandbox_policy=policy)
        self._applications[package.manifest.name] = app
        if package.hooks.on_install:
            package.hooks.on_install(package.manifest)
        return f"Installed {package.manifest.name} in {sandbox.environment_path}"

    def uninstall(self, name: str) -> bool:
        app = self._applications.pop(name, None)
        if app and app.package.hooks.on_uninstall:
            app.package.hooks.on_uninstall(app.package.manifest)
        return app is not None

    def list_applications(self) -> Iterable[Application]:
        return list(self._applications.values())

    def launch(self, name: str) -> str:
        app = self._applications[name]
        return app.run()

    def register_hot_reload(self, name: str, callback: Callable[[], None]) -> None:
        self._watcher.watch(name, callback)

    async def trigger_hot_reload(self, name: str) -> None:
        await self._watcher.trigger(name)


# Built-in applications ---------------------------------------------------

def _notes_app() -> str:
    today = date.today().strftime("%Y-%m-%d")
    template = dedent(
        f"""
        Notes App
        ---------
        Today is {today}.
        • Capture ideas quickly and encrypt them in the Vault.
        • Use sync to back up your notes across Ragnar nodes.
        """
    ).strip()
    return template


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


def _news_app() -> str:
    headlines = [
        "Ragnar OS ships sandboxed app platform",
        "Service mesh discovers three peers on the LAN",
        "Marketplace introduces signed downloads",
    ]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["Daily Brief", "-----------", f"Updated: {now}"]
    lines.extend(f" • {headline}" for headline in headlines)
    return "\n".join(lines)


def _system_monitor_app() -> str:
    load = os.getpid()
    lines = ["System Monitor", "--------------"]
    lines.append(f"Process ID: {load}")
    lines.append("Health: Stable")
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


def _calendar_app() -> str:
    import calendar

    now = datetime.now()
    month_view = calendar.TextCalendar().formatmonth(now.year, now.month).rstrip()
    lines = ["Calendar Hub", "------------", month_view]
    return "\n".join(lines)


DEFAULT_PACKAGES: Dict[str, ApplicationPackage] = {}


def _register_default_package(name: str, entrypoint: Callable[[], str], permissions: Dict[str, bool]) -> None:
    manifest = AppManifest(
        name=name,
        version="1.0.0",
        description=f"Built-in {name} app",
        permissions=permissions,
        icon=f"{name.lower()}.png",
        hooks={"on_install": "notify", "on_update": "refresh", "on_uninstall": "cleanup"},
    )
    package = ApplicationPackage(manifest=manifest, entrypoint=entrypoint)
    DEFAULT_PACKAGES[name] = package


_register_default_package("Notes", _notes_app, {"fs": True, "ui": True})
_register_default_package("Calculator", _calculator_app, {"ui": True})
_register_default_package("Weather", _weather_app, {"network": True, "ui": True})
_register_default_package("Terminal", _terminal_app, {"fs": True, "ui": True})
_register_default_package("News", _news_app, {"network": True, "ui": True})
_register_default_package("System Monitor", _system_monitor_app, {"ui": True})
_register_default_package("Music", _music_app, {"ui": True})
_register_default_package("Calendar", _calendar_app, {"ui": True})


DEFAULT_APPLICATIONS: List[ApplicationPackage] = list(DEFAULT_PACKAGES.values())
