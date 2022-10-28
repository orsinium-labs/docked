from __future__ import annotations

import json
import shlex
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ._stage import Stage
    from ._types import BaseImage


def format_stage_name(stage: Stage | BaseImage) -> str:
    from ._stage import Stage
    if isinstance(stage, Stage):
        return stage.name
    return str(stage)


def format_shell_cmd(cmd: list[str] | str, *, shell: bool) -> str:
    """

    + `shell` form is when cmd is a string that gets passed into shell.
    + `exec` form is when cmd is a list that gets executed on its own.
    """
    # shell form
    if shell:
        if isinstance(cmd, str):
            return cmd
        return shlex.join(cmd)

    # exec form
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    return json.dumps(cmd)


def json_if_spaces(vals: list[str]) -> str:
    if any(' ' in val for val in vals):
        return json.dumps(vals)
    return ' '.join(vals)
