"""Ragnar package management tooling."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Dependency:
    name: str
    version: str


@dataclass
class Lockfile:
    dependencies: List[Dependency] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"dependencies": [dep.__dict__ for dep in self.dependencies]}

    def compute_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode("utf8")).hexdigest()


class OfflineMirror:
    """Represents an offline dependency mirror archive."""

    def __init__(self, archive: Path) -> None:
        self.archive = archive

    def describe(self) -> str:
        return f"Offline mirror at {self.archive}"


class RagnarPackageManager:
    """Small wrapper around pip like workflows (simulated)."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._installed: Dict[str, List[Dependency]] = {}
        self._lockfiles: Dict[str, Lockfile] = {}

    def install(self, app: str, dependencies: Iterable[Dependency]) -> Lockfile:
        deps = list(dependencies)
        self._installed[app] = deps
        lock = Lockfile(dependencies=deps)
        self._lockfiles[app] = lock
        return lock

    def rollback(self, app: str) -> None:
        self._installed.pop(app, None)
        self._lockfiles.pop(app, None)

    def get_lock(self, app: str) -> Optional[Lockfile]:
        return self._lockfiles.get(app)

    def installed(self, app: str) -> List[Dependency]:
        return self._installed.get(app, [])
