"""Boot sequence logic for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass

from .all_in_one import MiniOS
from .loading import FileLoader
from .maintenance import FileIntegrityVerifier


@dataclass
class BootReport:
    """Information gathered while booting the Mini OS."""

    steps: list[str]
    ready: bool

    def summary(self) -> str:
        status = "READY" if self.ready else "FAILED"
        lines = ["Boot sequence:"] + [f" - {step}" for step in self.steps]
        lines.append(f"Status: {status}")
        return "\n".join(lines)


def boot_sequence() -> tuple[MiniOS, BootReport]:
    """Perform a minimal boot sequence and return the running OS and report."""

    steps: list[str] = []
    steps.append("Initializing kernel stubs")
    steps.append("Loading device drivers (simulated)")
    steps.append("Starting system services")

    verifier = FileIntegrityVerifier.default_manifest()
    loader = FileLoader.from_manifest(verifier.expected_hashes)
    for entry in loader.load_all():
        steps.append(f"File load -> {entry}")

    integrity_ok, integrity_message = verifier.verify()
    steps.append(integrity_message)

    os_instance = MiniOS(integrity_verifier=verifier)
    steps.append("MiniOS core initialized")

    maintenance_steps = os_instance.run_auto_maintenance()
    for entry in maintenance_steps:
        steps.append(f"Maintenance: {entry}")

    security_steps = os_instance.run_security_suite()
    for entry in security_steps:
        steps.append(f"Security: {entry}")

    report = BootReport(steps=steps, ready=integrity_ok)
    return os_instance, report
