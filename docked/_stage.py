from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, Iterator

from ._steps import BuildStep, RunStep, Step


if TYPE_CHECKING:
    from ._types import BaseImage


class Stage:
    """A single stage of the build.

    Represents everything from FROM to FROM (or end of file) in Dockerfile.

    Many arguments might appear as they would better fit into Image,
    but not really. One Image can produce multiple container images
    when using multi-stage builds. And depending on which Stage you target,
    the correspoding arguments (like labels) might be different.

    Args:
        base: base image to use or a previous Stage to start from.
        name: the Stage name. Must be specified and unique for multi-stage builds.
        platform: the platform for which to build the image.
        build: Steps to execute when building the image.
        run: Steps that affect how container based on the image will be ran.
        labels: meta information associated with the resulting image.
            Corresponds to LABEL instruction in Dockerfile.
    """
    __slots__ = ('name', 'base', 'platform', 'build', 'run', 'labels')

    def __init__(
        self,
        *,
        base: BaseImage | Stage,
        name: str = 'main',
        platform: str | None = None,
        build: list[BuildStep] | None = None,
        run: list[RunStep] | None = None,
        labels: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.base = base
        self.platform = platform
        self.build = build or []
        self.run = run or []
        self.labels = labels or {}

    def as_str(self) -> str:
        """Represent the stage as valid Dockerfile syntax.
        """
        return '\n'.join(self.iter_lines())

    def iter_lines(self) -> Iterator[str]:
        """Emit lines of Dockerfile one-by-one.

        Useful for generating big stages without putting too much into memory.
        """
        yield self._from
        yield from self._labels
        step: Step
        for step in self.build:
            yield step.as_str()
        for step in self.run:
            yield step.as_str()

    @property
    def all_steps(self) -> Iterator[Step]:
        """Iterate over all steps, from both ``build`` and ``run``.
        """
        yield from self.build
        yield from self.run

    @property
    def min_version(self) -> str:
        """The minimal syntax version required for the Stage.
        """
        versions = (step.min_version for step in chain(self.build, self.run))
        return max(versions, default='1.0')

    @property
    def _from(self) -> str:
        result = 'FROM'
        if self.platform:
            result += f' --platform={self.platform}'
        result += f' {self.base}'
        if self.name:
            result += f' AS {self.name}'
        return result

    @property
    def _labels(self) -> Iterator[str]:
        for name, value in self.labels.items():
            if not value or ' ' in value:
                yield f'LABEL {name}="{value}"'
            else:
                yield f'LABEL {name}={value}'

    def __str__(self) -> str:
        return self.as_str()
