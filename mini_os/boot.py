"""Boot sequence logic for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass

from .all_in_one import MiniOS


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

    os_instance = MiniOS()
    steps.append("MiniOS core initialized")

    report = BootReport(steps=steps, ready=True)
    return os_instance, report
