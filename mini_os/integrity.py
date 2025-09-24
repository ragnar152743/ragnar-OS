"""File integrity verification for the MiniOS boot process."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class IntegrityIssue:
    path: Path
    reason: str
    expected_hash: str | None = None
    actual_hash: str | None = None


@dataclass
class IntegrityReport:
    checked_files: List[Path]
    issues: List[IntegrityIssue]

    @property
    def healthy(self) -> bool:
        return not self.issues

    def summary(self) -> str:
        lines = ["Integrity check:"]
        for path in self.checked_files:
            lines.append(f" - {path}")
        if self.healthy:
            lines.append("All monitored files match expected hashes.")
        else:
            lines.append("Issues detected:")
            for issue in self.issues:
                detail = f" * {issue.path}: {issue.reason}"
                if issue.expected_hash and issue.actual_hash:
                    detail += f" (expected {issue.expected_hash}, got {issue.actual_hash})"
                lines.append(detail)
        return "\n".join(lines)


class IntegrityChecker:
    """Validate repository files against an integrity manifest."""

    def __init__(self, base_path: Path | None = None, manifest_name: str = "integrity_manifest.json") -> None:
        self.base_path = Path(base_path or Path(__file__).resolve().parent.parent)
        self.manifest_path = self.base_path / manifest_name

    def _load_manifest(self) -> dict[str, str]:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Integrity manifest not found: {self.manifest_path}")
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {key: value for key, value in data.items()}

    def _hash_file(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify(self, files: Iterable[str] | None = None) -> IntegrityReport:
        manifest = self._load_manifest()
        targets = list(files) if files is not None else list(manifest.keys())
        issues: list[IntegrityIssue] = []
        checked: list[Path] = []

        for relative in targets:
            expected_hash = manifest.get(relative)
            path = self.base_path / relative
            if expected_hash is None:
                issues.append(
                    IntegrityIssue(path=path, reason="No expected hash available in manifest.")
                )
                continue
            if not path.exists():
                issues.append(
                    IntegrityIssue(path=path, reason="File missing.", expected_hash=expected_hash)
                )
                continue

            actual_hash = self._hash_file(path)
            checked.append(path)
            if actual_hash != expected_hash:
                issues.append(
                    IntegrityIssue(
                        path=path,
                        reason="Hash mismatch.",
                        expected_hash=expected_hash,
                        actual_hash=actual_hash,
                    )
                )

        return IntegrityReport(checked_files=checked, issues=issues)

