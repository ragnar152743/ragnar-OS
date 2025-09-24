"""Security, sandboxing, and virtual storage facilities for Ragnar Mini OS."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence


def _hash_file(path: Path) -> str:
    """Return the SHA-256 hash for *path*.

    A compact helper so the antivirus engine and storage layers can share a
    consistent hashing implementation without importing maintenance internals.
    """

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class ScanObservation:
    """Represents the outcome of scanning a single file."""

    path: str
    status: str
    reason: str


class AntivirusEngine:
    """Perform lightweight antivirus and tamper checks."""

    def __init__(self, verifier: Optional["FileIntegrityVerifier"] = None) -> None:
        # A verifier allows us to reuse the existing integrity manifest so we do
        # not have to maintain separate hash catalogs.
        self._verifier = verifier
        self._quarantine: Dict[str, str] = {}

    @property
    def quarantined_items(self) -> Dict[str, str]:
        """Return the current quarantine inventory keyed by file path."""

        return dict(self._quarantine)

    def scan(self, extra_targets: Optional[Sequence[Path]] = None) -> List[ScanObservation]:
        """Scan known files and optional *extra_targets*.

        For simplicity we treat mismatched hashes or missing files as
        quarantinable events and reuse the integrity manifest hashes when
        available. Extra targets provide a hook for ad-hoc scanning during
        development or testing.
        """

        observations: List[ScanObservation] = []

        if self._verifier is not None:
            root = self._verifier.root_directory
            for relative, expected_hash in self._verifier.expected_hashes.items():
                absolute = root / relative
                if not absolute.exists():
                    observations.append(
                        ScanObservation(relative, "missing", "File is absent from disk"),
                    )
                    continue

                actual_hash = _hash_file(absolute)
                if actual_hash != expected_hash:
                    self._quarantine[relative] = actual_hash
                    observations.append(
                        ScanObservation(
                            relative,
                            "quarantined",
                            "Hash mismatch compared to manifest",
                        ),
                    )
                else:
                    observations.append(
                        ScanObservation(relative, "clean", "Hash matches manifest"),
                    )

        for target in extra_targets or []:
            if not target.exists():
                observations.append(
                    ScanObservation(str(target), "missing", "Extra target not found"),
                )
                continue

            if target.is_file():
                size = target.stat().st_size
                if size == 0:
                    status, reason = "suspicious", "Empty file flagged for review"
                else:
                    status, reason = "clean", "No anomalies detected"
                observations.append(ScanObservation(str(target), status, reason))

        return observations

    def summarize(self, observations: Sequence[ScanObservation]) -> str:
        """Produce a human friendly summary of *observations*."""

        quarantined = sum(1 for entry in observations if entry.status == "quarantined")
        suspicious = sum(1 for entry in observations if entry.status == "suspicious")
        clean = sum(1 for entry in observations if entry.status == "clean")
        missing = sum(1 for entry in observations if entry.status == "missing")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            "Antivirus scan @ {timestamp}: {clean} clean, {quarantined} quarantined, "
            "{suspicious} suspicious, {missing} missing."
        ).format(
            timestamp=timestamp,
            clean=clean,
            quarantined=quarantined,
            suspicious=suspicious,
            missing=missing,
        )


@dataclass
class SandboxPolicy:
    """Declarative permissions describing how an app may interact with the OS."""

    app_name: str
    allowed_paths: List[Path] = field(default_factory=list)
    allow_network: bool = False
    allow_ui: bool = True

    def allows_path(self, candidate: Path) -> bool:
        candidate = candidate.resolve()
        for allowed in self.allowed_paths:
            try:
                candidate.relative_to(allowed.resolve())
            except ValueError:
                continue
            return True
        return False


class SandboxManager:
    """Registry for sandbox policies and execution helpers."""

    def __init__(self) -> None:
        self._policies: Dict[str, SandboxPolicy] = {}

    def register_policy(
        self,
        app_name: str,
        allowed_paths: Iterable[Path],
        *,
        allow_network: bool = False,
        allow_ui: bool = True,
    ) -> SandboxPolicy:
        policy = SandboxPolicy(
            app_name=app_name,
            allowed_paths=[Path(path).resolve() for path in allowed_paths],
            allow_network=allow_network,
            allow_ui=allow_ui,
        )
        self._policies[app_name] = policy
        return policy

    def get_policy(self, app_name: str) -> SandboxPolicy:
        if app_name not in self._policies:
            raise KeyError(f"No sandbox policy registered for {app_name!r}")
        return self._policies[app_name]

    def ensure_policy(self, app_name: str, allowed_paths: Iterable[Path]) -> SandboxPolicy:
        if app_name not in self._policies:
            return self.register_policy(app_name, allowed_paths)
        return self._policies[app_name]

    def describe(self) -> str:
        policies = list(self._policies.values())
        if not policies:
            return "Sandbox: no policies registered."
        descriptions = []
        for policy in policies:
            network = "net" if policy.allow_network else "isolated"
            descriptions.append(
                f"{policy.app_name} ({network}, {len(policy.allowed_paths)} paths)",
            )
        joined = "; ".join(descriptions)
        return f"Sandbox policies active -> {joined}."

    @contextmanager
    def activated(self, app_name: str) -> Iterator[SandboxPolicy]:
        policy = self.get_policy(app_name)
        yield policy


@dataclass
class VirtualVolume:
    """Represents a logical storage volume inside the virtual storage manager."""

    name: str
    root: Path
    quota_bytes: int

    def usage_bytes(self) -> int:
        total = 0
        for candidate in self.root.rglob("*"):
            if candidate.is_file():
                total += candidate.stat().st_size
        return total


class VirtualStorageManager:
    """Lightweight logical volume manager backed by the host filesystem."""

    def __init__(self, base_directory: Optional[Path] = None) -> None:
        self._base = Path(base_directory or Path.cwd() / ".ragnar_storage").resolve()
        self._base.mkdir(parents=True, exist_ok=True)
        self._volumes: Dict[str, VirtualVolume] = {}

    @property
    def base_directory(self) -> Path:
        return self._base

    def ensure_volume(self, name: str, quota_bytes: int) -> VirtualVolume:
        if name in self._volumes:
            volume = self._volumes[name]
            if volume.quota_bytes != quota_bytes:
                self._volumes[name] = VirtualVolume(name, volume.root, quota_bytes)
            return self._volumes[name]

        root = self._base / name
        root.mkdir(parents=True, exist_ok=True)
        volume = VirtualVolume(name=name, root=root, quota_bytes=quota_bytes)
        self._volumes[name] = volume
        return volume

    def get_volume(self, name: str) -> VirtualVolume:
        if name not in self._volumes:
            raise KeyError(f"No virtual volume named {name!r}")
        return self._volumes[name]

    def write_text(self, volume_name: str, relative_path: str, content: str) -> Path:
        volume = self.get_volume(volume_name)
        encoded = content.encode("utf-8")
        destination = (volume.root / relative_path).resolve()
        if volume.root not in destination.parents and destination != volume.root:
            raise ValueError("Attempted to write outside of the virtual volume boundary")

        existing_size = destination.stat().st_size if destination.exists() else 0
        usage = volume.usage_bytes() - existing_size
        if usage + len(encoded) > volume.quota_bytes:
            raise RuntimeError(
                f"Writing to {relative_path} would exceed quota for volume {volume_name}",
            )

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(encoded)
        return destination

    def list_volumes(self) -> List[VirtualVolume]:
        return list(self._volumes.values())

    def describe(self) -> str:
        volumes = self.list_volumes()
        if not volumes:
            return "Virtual storage: no volumes provisioned."
        parts = []
        for volume in volumes:
            used = volume.usage_bytes()
            parts.append(
                f"{volume.name} ({used}/{volume.quota_bytes} bytes) -> {volume.root}",
            )
        return "Virtual storage volumes -> " + "; ".join(parts)


__all__ = [
    "AntivirusEngine",
    "SandboxManager",
    "SandboxPolicy",
    "ScanObservation",
    "VirtualStorageManager",
    "VirtualVolume",
]
