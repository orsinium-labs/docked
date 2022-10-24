from __future__ import annotations

from ._steps import ARG, FROM, Instruction


class Stage:
    __slots__ = ('steps', )
    steps: tuple[Instruction, ...]

    def __init__(self, first: FROM | ARG, *rest: Instruction) -> None:
        self.steps = (first, ) + rest

    def as_str(self) -> str:
        return '\n'.join(step.as_str() for step in self.steps)

    @property
    def name(self) -> str | None:
        for step in self.steps:
            if isinstance(step, FROM):
                return step.name
        return None

    @property
    def min_version(self) -> str:
        versions = (step.min_version for step in self.steps)
        return max(versions, default='1.0')

    def __str__(self) -> str:
        return self.as_str()
