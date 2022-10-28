"""

Ideas for checks come from these linters:
    https://github.com/replicatedhq/dockerfilelint
    https://github.com/hadolint/hadolint
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from functools import singledispatch
from typing import Iterator

from .. import _steps as steps
from . import _violations as vs
from ._violation import Violation


BAD_COMMANDS = frozenset({
    'free',
    'kill',
    'mount',
    'nano',
    'ps',
    'service',
    'shutdown',
    'ssh',
    'top',
    'vi',
    'vim',
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
def check_step(step: steps.Step, ctx: Context) -> Iterator[Violation]:
    yield from ()


@check_step.register
def _(step: steps.WORKDIR, ctx: Context) -> Iterator[Violation]:
    if str(step.path).startswith('/'):
        return
    # TODO: support windows paths
    yield vs.WORKDIR_01


@check_step.register
def _(step: steps.RUN, ctx: Context) -> Iterator[Violation]:
    for cmd in (step.first,) + step.rest:
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        bin = cmd[0]
        if bin == 'sudo':
            yield vs.RUN_02
            if len(cmd) > 1:
                cmd = cmd[1:]
                bin = cmd[0]
        if bin in BAD_COMMANDS:
            yield vs.RUN_01.format(bin=bin)

        if bin in ('apt', 'apt-get'):
            if cmd[1] in ('upgrade', 'dist-upgrade'):
                yield vs.RUN_03.format(subcmd=cmd[1])
            if cmd[1] == 'update' and not step.rest:
                yield vs.RUN_04


@check_step.register
def _(step: steps.USER, ctx: Context) -> Iterator[Violation]:
    if ctx.is_last and step.user in (0, 'root'):
        yield vs.USER_01


@check_step.register
def _(step: steps.CMD, ctx: Context) -> Iterator[Violation]:
    if not ctx.is_last:
        yield vs.CMD_01
    if step.shell:
        yield vs.CMD_02


@check_step.register
def _(step: steps.EXPOSE, ctx: Context) -> Iterator[Violation]:
    if not 0 < step.port < 65535:
        yield vs.EXPOSE_01
