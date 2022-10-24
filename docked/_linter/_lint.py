from __future__ import annotations
from typing import TYPE_CHECKING, Iterator

from ._checks import check_step, Context

if TYPE_CHECKING:
    from .._image import Image
    from ._violation import Violation


def lint(image: Image) -> Iterator[Violation]:
    for stage in image.stages:
        ctx = Context(
            steps=tuple(type(step).__name__ for step in stage.steps),
            index=0,
        )
        for i, step in enumerate(stage.steps):
            ctx.index = i
            yield from check_step(step, ctx)
