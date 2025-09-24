"""Marketplace integration for installing Ragnar apps."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from .applications import ApplicationPackage


@dataclass
class MarketplaceEntry:
    name: str
    version: str
    hash: str
    signature: str
    description: str


class MarketplaceClient:
    def __init__(self, feed: Path) -> None:
        self.feed = feed
        self.feed.parent.mkdir(parents=True, exist_ok=True)
        if not self.feed.exists():
            self.feed.write_text(json.dumps([], indent=2))

    def list_entries(self) -> List[MarketplaceEntry]:
        data = json.loads(self.feed.read_text())
        return [MarketplaceEntry(**item) for item in data]


class AppInstaller:
    """Installs applications from a marketplace feed."""

    def __init__(self, marketplace: MarketplaceClient) -> None:
        self.marketplace = marketplace

    def install(self, name: str, available: Dict[str, ApplicationPackage]) -> ApplicationPackage:
        entries = {entry.name: entry for entry in self.marketplace.list_entries()}
        if name not in entries:
            raise KeyError(name)
        if name not in available:
            raise KeyError(f"Package {name} not bundled")
        return available[name]
