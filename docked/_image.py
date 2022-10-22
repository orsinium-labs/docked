from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._stage import Stage


DEFAULT_CHANNEL = 'docker/dockerfile'


class Image:
    __slots__ = ('stages', 'syntax_channel', 'syntax_version', 'escape')

    def __init__(
        self,
        first: Stage, *rest: Stage,
        syntax_channel: str = DEFAULT_CHANNEL,
        syntax_version: str | None = None,
        escape: str = '\\',
    ) -> None:
        if syntax_channel != DEFAULT_CHANNEL and not syntax_version:
            raise ValueError('syntax_version is required with non-default syntax_channel')
        self.stages = (first,) + rest
        self.syntax_channel = syntax_channel
        self.syntax_version = syntax_version
        self.escape = escape

    @property
    def min_version(self) -> str:
        versions = (stage.min_version for stage in self.stages)
        return max(versions, default='1.0')

    @property
    def syntax(self) -> str:
        return f'{self.syntax_channel}:{self.min_version}'

    def as_str(self) -> str:
        result: list[str] = [f'# syntax={self.syntax}\nescape={self.escape}']
        result.extend(stage.as_str() for stage in self.stages)
        return '\n\n'.join(result)

    def __str__(self) -> str:
        return self.as_str()
