from __future__ import annotations
from itertools import chain
from typing import Iterator

from ._steps import BuildStep, RunStep, Step, FROM


class Stage:
    __slots__ = ('build', 'run')

    def __init__(
        self, *,
        build: list[BuildStep] | None = None,
        run: list[RunStep] | None = None,
    ) -> None:
        self.build = build or []
        self.run = run or []

    def as_str(self) -> str:
        return '\n'.join(self.iter_lines())

    def iter_lines(self) -> Iterator[str]:
        step: Step
        for step in self.build:
            yield step.as_str()
        for step in self.run:
            yield step.as_str()

    @property
    def name(self) -> str | None:
        for step in self.build:
            if isinstance(step, FROM):
                return step.name
        return None

    @property
    def all_steps(self) -> Iterator[Step]:
        yield from self.build
        yield from self.run

    @property
    def min_version(self) -> str:
        versions = (step.min_version for step in chain(self.build, self.run))
        return max(versions, default='1.0')

    def __str__(self) -> str:
        return self.as_str()
