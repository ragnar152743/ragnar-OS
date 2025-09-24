"""Security services for the Ragnar Mini OS simulation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional


def _pbkdf2(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf8"), salt, iterations)


@dataclass
class PasswordRecord:
    username: str
    salt: bytes
    hashed: bytes


class PasswordHasher:
    """Utility that stores PBKDF2 salted password records."""

    def __init__(self, pepper: Optional[str] = None) -> None:
        self._pepper = pepper or "ragnar-pepper"
        self._records: Dict[str, PasswordRecord] = {}

    def register(self, username: str, password: str) -> PasswordRecord:
        salt = os.urandom(16)
        hashed = _pbkdf2(password + self._pepper, salt)
        record = PasswordRecord(username=username, salt=salt, hashed=hashed)
        self._records[username] = record
        return record

    def verify(self, username: str, password: str) -> bool:
        record = self._records.get(username)
        if record is None:
            return False
        expected = record.hashed
        candidate = _pbkdf2(password + self._pepper, record.salt)
        return hmac.compare_digest(expected, candidate)


class LocalLoginManager:
    """Handles authentication for local profiles."""

    def __init__(self, hasher: PasswordHasher) -> None:
        self._hasher = hasher
        self._sessions: Dict[str, str] = {}

    def sign_up(self, username: str, password: str) -> None:
        self._hasher.register(username, password)

    def login(self, username: str, password: str) -> bool:
        if self._hasher.verify(username, password):
            token = base64.urlsafe_b64encode(os.urandom(18)).decode("ascii")
            self._sessions[token] = username
            return True
        return False

    def session_owner(self, token: str) -> Optional[str]:
        return self._sessions.get(token)


@dataclass
class ApiKey:
    app: str
    key: str
    scopes: Iterable[str]


class ApiKeyRegistry:
    """Assigns minimal capability keys to applications."""

    def __init__(self) -> None:
        self._keys: Dict[str, ApiKey] = {}

    def issue(self, app: str, scopes: Iterable[str]) -> ApiKey:
        key = base64.urlsafe_b64encode(os.urandom(24)).decode("ascii")
        api_key = ApiKey(app=app, key=key, scopes=tuple(scopes))
        self._keys[app] = api_key
        return api_key

    def validate(self, app: str, key: str, scope: str) -> bool:
        record = self._keys.get(app)
        return bool(record and record.key == key and scope in record.scopes)


@dataclass
class PermissionDeclaration:
    fs: bool = False
    network: bool = False
    ui: bool = True
    usb: bool = False


class PermissionRegistry:
    """Stores declarative permission manifests."""

    def __init__(self) -> None:
        self._permissions: Dict[str, PermissionDeclaration] = {}

    def declare(self, app: str, manifest: PermissionDeclaration) -> None:
        self._permissions[app] = manifest

    def is_allowed(self, app: str, capability: str) -> bool:
        manifest = self._permissions.get(app)
        if manifest is None:
            return False
        return bool(getattr(manifest, capability, False))


class Vault:
    """Stores encrypted secrets per user or application."""

    def __init__(self, storage_dir: Path) -> None:
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _derive_key(self, name: str, length: int) -> bytes:
        digest = hashlib.sha256(name.encode("utf8")).digest()
        repeats = (length // len(digest)) + 1
        return (digest * repeats)[:length]

    def store(self, name: str, secret: str) -> Path:
        secret_bytes = secret.encode("utf8")
        key = self._derive_key(name, len(secret_bytes))
        payload = bytes(a ^ b for a, b in zip(secret_bytes, key))
        encoded = base64.urlsafe_b64encode(payload)
        target = self._storage_dir / f"{name}.secret"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
        return target

    def load(self, name: str) -> Optional[str]:
        target = self._storage_dir / f"{name}.secret"
        if not target.exists():
            return None
        payload = base64.urlsafe_b64decode(target.read_bytes())
        key = self._derive_key(name, len(payload))
        secret_bytes = bytes(a ^ b for a, b in zip(payload, key))
        return secret_bytes.decode("utf8", errors="ignore")


@dataclass
class AuditEntry:
    timestamp: datetime
    actor: str
    action: str
    details: Dict[str, str]
    signature: str


class AuditLog:
    """Append-only signed log for sensitive events."""

    def __init__(self, key: str) -> None:
        self._key = key.encode("utf8")
        self._entries: list[AuditEntry] = []

    def append(self, actor: str, action: str, **details: str) -> AuditEntry:
        payload = json.dumps({"actor": actor, "action": action, **details}, sort_keys=True)
        signature = hmac.new(self._key, payload.encode("utf8"), hashlib.sha256).hexdigest()
        entry = AuditEntry(datetime.utcnow(), actor, action, details, signature)
        self._entries.append(entry)
        return entry

    def export(self) -> str:
        lines = []
        for entry in self._entries:
            lines.append(
                f"[{entry.timestamp.isoformat()}] {entry.actor}: {entry.action} {entry.details} (sig={entry.signature})"
            )
        return "\n".join(lines)


class AntivirusEngine:
    """Toy antivirus scanner that flags forbidden signatures."""

    def __init__(self) -> None:
        self._signatures = {"malware", "virus", "worm"}

    def scan(self, data: str) -> bool:
        needle = data.lower()
        return not any(signature in needle for signature in self._signatures)


class SandboxThreatMonitor:
    """Observes sandboxes for suspicious behaviour."""

    def __init__(self) -> None:
        self._alerts: list[str] = []

    def report(self, sandbox: str, event: str) -> None:
        self._alerts.append(f"{sandbox}: {event}")

    def alerts(self) -> list[str]:
        return list(self._alerts)
