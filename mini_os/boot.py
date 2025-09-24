"""Boot sequence logic for the Ragnar Mini OS."""

from __future__ import annotations

from dataclasses import dataclass

from .all_in_one import MiniOS
from .localization import LanguageManager
from .loading import FileLoader
from .maintenance import FileIntegrityVerifier


@dataclass
class BootReport:
    """Information gathered while booting the Mini OS."""

    steps: list[str]
    ready: bool
    splash: str
    language_manager: LanguageManager

    def summary(self) -> str:
        translator = self.language_manager.translate
        status_key = "boot_status_ready" if self.ready else "boot_status_failed"
        status = translator(status_key)
        lines = [translator("boot_summary_header")] + [f" - {step}" for step in self.steps]
        lines.append(translator("boot_summary_status", status=status))
        return "\n".join(lines)


def boot_sequence() -> tuple[MiniOS, BootReport]:
    """Perform a minimal boot sequence and return the running OS and report."""

    language_manager, language_steps = LanguageManager.load_or_initialize()
    translator = language_manager.translate

    steps: list[str] = []
    steps.extend(language_steps)
    steps.append(translator("boot_step_kernel"))
    steps.append(translator("boot_step_drivers"))
    steps.append(translator("boot_step_services"))

    verifier = FileIntegrityVerifier.default_manifest(language_manager=language_manager)
    loader = FileLoader.from_manifest(verifier.expected_hashes)
    for record in loader.load_all():
        if record.bytes_cached is None:
            steps.append(
                translator(
                    "boot_step_file_missing",
                    path=record.path,
                    index=record.index,
                    total=record.total,
                )
            )
        else:
            steps.append(
                translator(
                    "boot_step_file_loaded",
                    path=record.path,
                    index=record.index,
                    total=record.total,
                    size=record.bytes_cached,
                )
            )

    integrity_ok, integrity_message = verifier.verify()
    steps.append(integrity_message)

    os_instance = MiniOS(language_manager=language_manager, integrity_verifier=verifier)
    steps.append(translator("boot_step_core"))

    maintenance_steps = os_instance.run_auto_maintenance()
    for entry in maintenance_steps:
        steps.append(translator("maintenance_prefix", entry=entry))

    splash = os_instance.render_boot_splash(steps)

    report = BootReport(
        steps=steps,
        ready=integrity_ok,
        splash=splash,
        language_manager=language_manager,
    )
    return os_instance, report
