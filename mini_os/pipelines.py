"""No-code pipelines for chaining applications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List


@dataclass
class PipelineStep:
    name: str
    handler: Callable[[str], str]


class PipelineEngine:
    def __init__(self) -> None:
        self._steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> None:
        self._steps.append(step)

    def run(self, initial_input: str) -> str:
        data = initial_input
        for step in self._steps:
            data = step.handler(data)
        return data

    def describe(self) -> str:
        return " -> ".join(step.name for step in self._steps)
