from __future__ import annotations


class Step:
    """A single Dockerfile instruction.

    Some instructions can have multiple Steps associated with them,
    to have a single responsibility.
    """

    __slots__ = ()

    def as_str(self) -> str:
        raise NotImplementedError

    @property
    def min_version(self) -> str:
        return '1.0'

    def __str__(self) -> str:
        return self.as_str()

    def __repr__(self) -> str:
        return f'{type(self).__name__}(...)'


class BuildStep(Step):
    """Step that can be used in Stage.build.

    These are steps that directly executed when building an Image.
    """
    __slots__ = ()


class RunStep(Step):
    """Step that can be used in Stage.run.

    These are steps that aren't executed when building Image but rather affect
    how the container will be run.
    """
    __slots__ = ()
