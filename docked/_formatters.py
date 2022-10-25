from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._stage import Stage


def format_stage_name(stage: Stage | str) -> str:
    if isinstance(stage, str):
        return stage
    name = stage.name
    if name is None:
        raise ValueError('the stage must have a name to copy from it')
    return name
