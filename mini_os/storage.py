"""Storage facilities for Ragnar Mini OS."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass
class LogicalVolume:
    name: str
    mount_point: Path
    quota_mb: int
    used_mb: int = 0

    def describe(self) -> str:
        return f"{self.name}: {self.used_mb}/{self.quota_mb} MB at {self.mount_point}"


class LogicalVolumeManager:
    """Manages logical volumes implemented as directories."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._volumes: Dict[str, LogicalVolume] = {}
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def create(self, name: str, quota_mb: int) -> LogicalVolume:
        mount = self._base_dir / name
        mount.mkdir(parents=True, exist_ok=True)
        volume = LogicalVolume(name=name, mount_point=mount, quota_mb=quota_mb)
        self._volumes[name] = volume
        return volume

    def get(self, name: str) -> Optional[LogicalVolume]:
        return self._volumes.get(name)

    def list_volumes(self) -> Iterable[LogicalVolume]:
        return list(self._volumes.values())


@dataclass
class VirtualStorage:
    """Represents a thin-provisioned storage namespace."""

    name: str
    backing_volume: LogicalVolume
    snapshots: Dict[str, int] = field(default_factory=dict)

    def snapshot(self, label: str) -> None:
        self.snapshots[label] = self.backing_volume.used_mb


class VirtualStorageManager:
    def __init__(self) -> None:
        self._virtuals: Dict[str, VirtualStorage] = {}

    def create(self, name: str, backing: LogicalVolume) -> VirtualStorage:
        storage = VirtualStorage(name=name, backing_volume=backing)
        self._virtuals[name] = storage
        return storage

    def list(self) -> Iterable[VirtualStorage]:
        return list(self._virtuals.values())


class KvStore:
    """Per-application SQLite key-value store with simple migrations."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS migrations (name TEXT PRIMARY KEY)")

    def set(self, key: str, value: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value))

    def get(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = cursor.fetchone()
        return row[0] if row else None

    def run_migration(self, name: str, statements: Iterable[str]) -> None:
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT 1 FROM migrations WHERE name = ?", (name,))
            if cur.fetchone():
                return
            for stmt in statements:
                conn.execute(stmt)
            conn.execute("INSERT INTO migrations (name) VALUES (?)", (name,))


class TrashManager:
    """Tracks deleted files before purging."""

    def __init__(self, trash_dir: Path) -> None:
        self._trash_dir = trash_dir
        self._trash_dir.mkdir(parents=True, exist_ok=True)
        self._items: Dict[str, Path] = {}

    def move_to_trash(self, name: str, content: str) -> Path:
        target = self._trash_dir / name
        target.write_text(content)
        self._items[name] = target
        return target

    def restore(self, name: str) -> Optional[str]:
        target = self._items.get(name)
        if target and target.exists():
            return target.read_text()
        return None
