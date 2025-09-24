"""Networking helpers for Ragnar Mini OS."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class SyncEndpoint:
    url: str
    credential: str


class ProfileSyncService:
    """Synchronises profile archives with remote endpoints."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._endpoints: List[SyncEndpoint] = []

    def register_endpoint(self, url: str, credential: str) -> None:
        self._endpoints.append(SyncEndpoint(url, credential))

    def sync(self, username: str, data: Dict[str, str]) -> str:
        archive = self.root / f"{username}.json"
        archive.write_text(json.dumps(data, indent=2, sort_keys=True))
        return f"Synced {username} to {len(self._endpoints)} endpoints"


class ServiceMesh:
    """Discovers peers via a simulated mDNS registry."""

    def __init__(self) -> None:
        self._peers: Dict[str, str] = {}

    def announce(self, name: str, address: str) -> None:
        self._peers[name] = address

    def peers(self) -> Dict[str, str]:
        return dict(self._peers)


class PortForwarder:
    """Records safe port forwarding rules."""

    def __init__(self) -> None:
        self._rules: Dict[str, int] = {}

    def forward(self, app: str, port: int) -> None:
        self._rules[app] = port

    def rules(self) -> Dict[str, int]:
        return dict(self._rules)
