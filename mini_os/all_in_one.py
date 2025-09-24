"""High-level integration of Mini OS components."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from .applications import ApplicationManager, DEFAULT_APPLICATIONS, DEFAULT_PACKAGES
from .development import ApiContractValidator, DevConsole, Profiler, TestKit
from .interfaces import InterfaceManager, Widget
from .kernel import (
    IPCBus,
    ManagedProcess,
    ProcessManager,
    SandboxManager,
    SandboxPolicy,
    ServiceRecord,
    ServiceRegistry,
    VirtualizationManager,
)
from .maintenance import AutoMaintenanceGuardian, FileIntegrityVerifier
from .marketplace import AppInstaller, MarketplaceClient
from .networking import PortForwarder, ProfileSyncService, ServiceMesh
from .packages import Dependency, OfflineMirror, RagnarPackageManager
from .pipelines import PipelineEngine, PipelineStep
from .profiles import ProfileManager
from .security import (
    ApiKeyRegistry,
    AntivirusEngine,
    AuditLog,
    LocalLoginManager,
    PasswordHasher,
    PermissionDeclaration,
    PermissionRegistry,
    SandboxThreatMonitor,
    Vault,
)
from .storage import LogicalVolumeManager, TrashManager, VirtualStorageManager
from .ui import DesktopShell


@dataclass
class MiniOS:
    """Represents the running Mini OS environment."""

    integrity_verifier: FileIntegrityVerifier = field(
        default_factory=FileIntegrityVerifier.default_manifest
    )
    base_dir: Path = field(default_factory=lambda: Path("var/ragnar"))
    process_manager: ProcessManager = field(default_factory=ProcessManager)
    ipc_bus: IPCBus = field(default_factory=IPCBus)
    sandbox_manager: SandboxManager = field(default_factory=SandboxManager)
    antivirus: AntivirusEngine = field(default_factory=AntivirusEngine)
    threat_monitor: SandboxThreatMonitor = field(default_factory=SandboxThreatMonitor)
    password_hasher: PasswordHasher = field(default_factory=PasswordHasher)
    api_keys: ApiKeyRegistry = field(default_factory=ApiKeyRegistry)
    permission_registry: PermissionRegistry = field(default_factory=PermissionRegistry)
    audit_log: AuditLog = field(default_factory=lambda: AuditLog("ragnar-audit"))
    pipeline_engine: PipelineEngine = field(default_factory=PipelineEngine)
    dev_console: DevConsole = field(default_factory=DevConsole)
    profiler: Profiler = field(default_factory=Profiler)
    contract_validator: ApiContractValidator = field(default_factory=ApiContractValidator)
    testkit: TestKit = field(default_factory=TestKit)

    def __post_init__(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.interface_manager: InterfaceManager = InterfaceManager()
        self.desktop_shell: DesktopShell = DesktopShell()
        self.virtualization_manager: VirtualizationManager = VirtualizationManager(self.sandbox_manager)
        self.application_manager: ApplicationManager = ApplicationManager(self.sandbox_manager)
        self.service_registry: ServiceRegistry = ServiceRegistry(self.process_manager)
        self.profile_manager: ProfileManager = ProfileManager(self.base_dir / "profiles")
        self.vault: Vault = Vault(self.base_dir / "vault")
        self.package_manager: RagnarPackageManager = RagnarPackageManager(self.base_dir / "pkg-cache")
        self.offline_mirror: OfflineMirror = OfflineMirror(self.base_dir / "mirror.zip")
        self.trash_manager: TrashManager = TrashManager(self.base_dir / "trash")
        self.volume_manager: LogicalVolumeManager = LogicalVolumeManager(self.base_dir / "volumes")
        self.virtual_storage: VirtualStorageManager = VirtualStorageManager()
        self.sync_service: ProfileSyncService = ProfileSyncService(self.base_dir / "sync")
        self.mesh: ServiceMesh = ServiceMesh()
        self.port_forwarder: PortForwarder = PortForwarder()
        self.marketplace: MarketplaceClient = MarketplaceClient(self.base_dir / "marketplace.json")
        self.app_installer: AppInstaller = AppInstaller(self.marketplace)
        self.login_manager: LocalLoginManager = LocalLoginManager(self.password_hasher)
        self.maintenance_guardian: AutoMaintenanceGuardian = AutoMaintenanceGuardian(self)

        # Provision core services -------------------------------------------------
        self._bootstrap_profiles()
        self._bootstrap_security()
        self._bootstrap_storage()
        self._bootstrap_applications()
        self._bootstrap_services()
        self._bootstrap_pipelines()

    # Bootstrapping helpers -----------------------------------------------------

    def _bootstrap_profiles(self) -> None:
        self.profile_manager.create("admin")
        self.login_manager.sign_up("admin", "admin123")
        archive_message = self.sync_service.sync("admin", {"welcome": "Bienvenue"})
        self.dev_console.log(archive_message)
        self.mesh.announce("ragnar-admin", "192.168.0.2")

    def _bootstrap_security(self) -> None:
        self.vault.store("admin/api-token", "super-secret-token")
        for name, package in DEFAULT_PACKAGES.items():
            permissions = PermissionDeclaration(
                fs=package.manifest.permissions.get("fs", False),
                network=package.manifest.permissions.get("network", False),
                ui=package.manifest.permissions.get("ui", True),
                usb=package.manifest.permissions.get("usb", False),
            )
            self.permission_registry.declare(name, permissions)
            api_key = self.api_keys.issue(name, package.manifest.permissions.keys())
            self.audit_log.append("system", "issued_api_key", app=name, key=api_key.key)

    def _bootstrap_storage(self) -> None:
        volume = self.volume_manager.create("root", quota_mb=1024)
        self.virtual_storage.create("root-virtual", volume)
        self.virtualization_manager.provision(
            "storage-vm",
            SandboxPolicy(allowed_paths=(str(volume.mount_point),), network=False, ui=False),
        )
        self.trash_manager.move_to_trash("readme.txt", "Old configuration placeholder")

    def _bootstrap_applications(self) -> None:
        for package in DEFAULT_APPLICATIONS:
            if self.antivirus.scan(package.manifest.description):
                self.application_manager.install(package)
                self.desktop_shell.register_widget(
                    Widget(title=package.manifest.name, body=package.manifest.description)
                )
                self.interface_manager.register_widget(
                    Widget(title=package.manifest.name, body=package.manifest.description)
                )
                self.package_manager.install(
                    package.manifest.name,
                    [Dependency(name="example-lib", version="1.0.0")],
                )
        self.pipeline_engine.add_step(
            PipelineStep(
                name="Notes to News",
                handler=lambda text: text + "\nNews Digest Ready",
            )
        )

    def _bootstrap_services(self) -> None:
        async def telemetry_task() -> str:
            return "telemetry heartbeat"

        process = ManagedProcess(name="telemetry", target=telemetry_task)
        self.service_registry.register(ServiceRecord(name="telemetry", process=process))
        self.port_forwarder.forward("terminal", 2222)

    def _bootstrap_pipelines(self) -> None:
        self.contract_validator.register("notes", {"title": str, "content": str})
        self.dev_console.log(self.pipeline_engine.describe())

    # Public API ---------------------------------------------------------------

    def list_app_names(self) -> Iterable[str]:
        return (app.package.manifest.name for app in self.application_manager.list_applications())

    def open_application(self, name: str) -> str:
        return self.application_manager.launch(name)

    def render_home(self) -> str:
        return self.desktop_shell.render()

    def render_app_menu(self) -> str:
        return self.interface_manager.render_app_menu(self.list_app_names())

    def describe(self) -> str:
        return (
            "Ragnar MiniOS now bundles kernel primitives, sandboxed apps, "
            "package management, profile sync, and a desktop shell."
        )

    def run_auto_maintenance(self) -> List[str]:
        return self.maintenance_guardian.run_startup_jobs()
