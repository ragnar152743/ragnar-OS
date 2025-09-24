"""Boot sequence logic for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .all_in_one import MiniOS
from .integrity import IntegrityChecker, IntegrityIssue, IntegrityReport
from .update import UpdateSummary


@dataclass
class BootReport:
    """Information gathered while booting the Mini OS."""

    steps: list[str]
    ready: bool
    integrity: IntegrityReport
    updates: Optional[UpdateSummary]

    def summary(self) -> str:
        status = "READY" if self.ready else "FAILED"
        lines = ["Boot sequence:"] + [f" - {step}" for step in self.steps]
        lines.append(f"Status: {status}")
        lines.append("")
        lines.append(self.integrity.summary())
        if self.updates is not None and hasattr(self.updates, "render"):
            lines.append("")
            lines.append(self.updates.render())
        return "\n".join(lines)


def boot_sequence() -> tuple[MiniOS, BootReport]:
    """Perform a minimal boot sequence and return the running OS and report."""

    steps: list[str] = []
    steps.append("Initializing kernel stubs")
    steps.append("Loading device drivers (simulated)")

    checker = IntegrityChecker()
    try:
        integrity_report = checker.verify()
        steps.append("Integrity manifest loaded")
        steps.append(
            "Integrity verification passed"
            if integrity_report.healthy
            else "Integrity verification failed"
        )
    except FileNotFoundError as exc:  # pragma: no cover - defensive branch
        issue = IntegrityIssue(path=checker.manifest_path if hasattr(checker, "manifest_path") else Path("integrity_manifest.json"), reason=str(exc))
        integrity_report = IntegrityReport(checked_files=[], issues=[issue])
        steps.append("Integrity manifest missing")

    steps.append("Starting system services")
    os_instance = MiniOS()
    steps.append("MiniOS core initialized")

    update_summary = os_instance.last_update_summary
    if update_summary:
        steps.append("Automatic updates executed")

    ready = integrity_report.healthy
    report = BootReport(
        steps=steps,
        ready=ready,
        integrity=integrity_report,
        updates=update_summary,
    )
    return os_instance, report
