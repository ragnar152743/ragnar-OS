"""Kernel-inspired primitives for the Ragnar Mini OS simulation."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Awaitable, Callable, Deque, Dict, Iterable, Optional


class ProcessError(RuntimeError):
    """Raised when a managed process fails."""


@dataclass
class ManagedProcess:
    """Represents a lightweight asynchronous process."""

    name: str
    target: Callable[[], Awaitable[str]]
    last_result: Optional[str] = None
    failures: int = 0

    async def run(self) -> str:
        try:
            self.last_result = await self.target()
            self.failures = 0
        except Exception as exc:  # pragma: no cover - demonstration safety
            self.failures += 1
            raise ProcessError(f"{self.name} crashed: {exc}") from exc
        return self.last_result


class ProcessManager:
    """Co-ordinates starting and stopping managed processes."""

    def __init__(self) -> None:
        self._processes: Dict[str, ManagedProcess] = {}

    def register(self, process: ManagedProcess) -> None:
        self._processes[process.name] = process

    def unregister(self, name: str) -> None:
        self._processes.pop(name, None)

    async def run_all(self) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for name, process in list(self._processes.items()):
            results[name] = await process.run()
        return results


@dataclass
class IPCMessage:
    sender: str
    channel: str
    payload: str


class IPCBus:
    """Very small message bus built on asyncio queues."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, asyncio.Queue[IPCMessage]] = {}

    def subscribe(self, channel: str) -> asyncio.Queue[IPCMessage]:
        queue: asyncio.Queue[IPCMessage] = asyncio.Queue()
        self._subscribers.setdefault(channel, queue)
        return queue

    async def publish(self, message: IPCMessage) -> None:
        queue = self._subscribers.get(message.channel)
        if queue is not None:
            await queue.put(message)


@dataclass
class ServiceRecord:
    name: str
    process: ManagedProcess
    restarts: int = 0
    status: str = "DOWN"


class ServiceRegistry:
    """Tracks services and restarts unhealthy ones automatically."""

    def __init__(self, process_manager: ProcessManager) -> None:
        self._process_manager = process_manager
        self._records: Dict[str, ServiceRecord] = {}
        self._history: Deque[str] = deque(maxlen=50)

    def register(self, record: ServiceRecord) -> None:
        self._records[record.name] = record
        self._process_manager.register(record.process)
        self._history.append(f"Registered service {record.name}")

    async def monitor(self) -> None:
        for record in self._records.values():
            try:
                await record.process.run()
                record.status = "UP"
                self._history.append(f"Service {record.name} healthy")
            except ProcessError:
                record.restarts += 1
                record.status = "RESTARTING"
                self._history.append(f"Service {record.name} restarting")
                await record.process.run()
                record.status = "UP"

    def history(self) -> Iterable[str]:
        return list(self._history)


@dataclass
class SandboxPolicy:
    allowed_paths: Iterable[str]
    denied_paths: Iterable[str] = ()
    network: bool = False
    ui: bool = True


@dataclass
class Sandbox:
    name: str
    policy: SandboxPolicy
    environment_path: str
    active: bool = False

    def enter(self) -> None:
        self.active = True

    def exit(self) -> None:
        self.active = False


class SandboxManager:
    """Manages per-application sandboxes."""

    def __init__(self) -> None:
        self._sandboxes: Dict[str, Sandbox] = {}

    def create(self, name: str, policy: SandboxPolicy) -> Sandbox:
        sandbox = Sandbox(name=name, policy=policy, environment_path=f".venv/{name}")
        sandbox.enter()
        self._sandboxes[name] = sandbox
        return sandbox

    def get(self, name: str) -> Optional[Sandbox]:
        return self._sandboxes.get(name)

    def enforce(self, name: str, path: str) -> bool:
        sandbox = self._sandboxes.get(name)
        if sandbox is None:
            return False
        if any(path.startswith(denied) for denied in sandbox.policy.denied_paths):
            return False
        if sandbox.policy.allowed_paths:
            return any(path.startswith(allowed) for allowed in sandbox.policy.allowed_paths)
        return True


@dataclass
class VirtualMachine:
    """Represents an isolated execution container for heavy workloads."""

    name: str
    sandbox: Sandbox
    running: bool = False

    def start(self) -> None:
        self.sandbox.enter()
        self.running = True

    def stop(self) -> None:
        self.sandbox.exit()
        self.running = False


class VirtualizationManager:
    """Creates and tracks virtual machines backed by sandboxes."""

    def __init__(self, sandbox_manager: SandboxManager) -> None:
        self._sandbox_manager = sandbox_manager
        self._machines: Dict[str, VirtualMachine] = {}

    def provision(self, name: str, policy: SandboxPolicy) -> VirtualMachine:
        sandbox = self._sandbox_manager.create(name, policy)
        vm = VirtualMachine(name=name, sandbox=sandbox)
        vm.start()
        self._machines[name] = vm
        return vm

    def status(self) -> Dict[str, str]:
        return {name: ("running" if vm.running else "stopped") for name, vm in self._machines.items()}
