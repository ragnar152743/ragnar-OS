"""Profile and ACL management for Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class AccessControlList:
    """Represents read/write/execute permissions."""

    read: List[str] = field(default_factory=list)
    write: List[str] = field(default_factory=list)
    execute: List[str] = field(default_factory=list)

    def grant(self, permission: str, path: str) -> None:
        getattr(self, permission).append(path)

    def can(self, permission: str, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in getattr(self, permission))


@dataclass
class UserProfile:
    username: str
    home: Path
    acl: AccessControlList = field(default_factory=AccessControlList)

    def ensure_home(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)


class ProfileManager:
    """Maintains multiple user profiles with isolated homes."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._profiles: Dict[str, UserProfile] = {}
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def create(self, username: str) -> UserProfile:
        profile = UserProfile(username=username, home=self._base_dir / username)
        profile.ensure_home()
        profile.acl.grant("read", str(profile.home))
        profile.acl.grant("write", str(profile.home))
        self._profiles[username] = profile
        return profile

    def get(self, username: str) -> Optional[UserProfile]:
        return self._profiles.get(username)

    def list_profiles(self) -> Iterable[UserProfile]:
        return list(self._profiles.values())
