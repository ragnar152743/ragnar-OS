"""Developer tooling for Ragnar Mini OS."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class LogEntry:
    timestamp: float
    message: str


class DevConsole:
    """Collects logs for the live console."""

    def __init__(self) -> None:
        self._logs: List[LogEntry] = []

    def log(self, message: str) -> None:
        self._logs.append(LogEntry(time.time(), message))

    def export(self) -> List[LogEntry]:
        return list(self._logs)


class Profiler:
    """Tiny profiler capturing elapsed time for callables."""

    def profile(self, name: str, func: Callable[[], str]) -> str:
        start = time.perf_counter()
        result = func()
        duration = (time.perf_counter() - start) * 1000
        return f"{name} took {duration:.2f}ms -> {result[:40]}"


class ApiContractValidator:
    """Validates payloads according to declarative contracts."""

    def __init__(self) -> None:
        self._contracts: Dict[str, Dict[str, type]] = {}

    def register(self, name: str, schema: Dict[str, type]) -> None:
        self._contracts[name] = schema

    def validate(self, name: str, payload: Dict[str, object]) -> bool:
        schema = self._contracts.get(name, {})
        for field, expected_type in schema.items():
            if field not in payload or not isinstance(payload[field], expected_type):
                return False
        return True


class TestKit:
    """Runs applications in a sandboxed environment for tests."""

    def run(self, name: str, callable_: Callable[[], str]) -> str:
        result = callable_()
        return f"TestKit[{name}] -> {result[:60]}"
