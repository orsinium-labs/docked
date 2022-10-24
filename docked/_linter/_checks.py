"""

Ideas for checks come from these linters:
    https://github.com/replicatedhq/dockerfilelint
    https://github.com/hadolint/hadolint
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import singledispatch
from typing import Iterator
from ._violation import Violation
from . import _violations as vs
from .. import _instructions as steps


BAD_COMMANDS = frozenset({
    "free",
    "kill",
    "mount",
    "ps",
    "service",
    "shutdown",
    "ssh",
    "top",
    "vim",
})


@dataclass
class Context:
    steps: tuple[str, ...]
    index: int

    @property
    def step(self) -> str:
        return self.steps[self.index]

    @property
    def is_first(self) -> bool:
        return self.steps.index(self.step) == self.index

    @property
    def is_last(self) -> bool:
        last_index = len(self.steps) - self.steps[::-1].index(self.step) - 1
        return last_index == self.index


@singledispatch
def check_step(step: steps.Instruction, ctx: Context) -> Iterator[Violation]:
    yield from ()


@check_step.register
def _(step: steps.FROM, ctx: Context) -> Iterator[Violation]:
    before = set(ctx.steps[:ctx.index]) - {'ARG'}
    for step_name in before:
        yield vs.FROM_01.format(step=step_name)
    if not step.image:
        yield vs.FROM_04
    if step.image != 'scratch' and not step.digest:
        if not step.tag:
            yield vs.FROM_02
        if step.tag == 'latest':
            yield vs.FROM_03


@check_step.register
def _(step: steps.WORKDIR, ctx: Context) -> Iterator[Violation]:
    if str(step.path).startswith('/'):
        return
    # TODO: support windows paths
    yield vs.V3000


@check_step.register
def _(step: steps.RUN, ctx: Context) -> Iterator[Violation]:
    for cmd in (step.first,) + step.rest:
        if isinstance(cmd, list):
            bin = cmd[0]
        else:
            bin = cmd.split()[0]
        if bin in BAD_COMMANDS:
            yield vs.V3001.format(bin=bin)


@check_step.register
def _(step: steps.USER, ctx: Context) -> Iterator[Violation]:
    ...
