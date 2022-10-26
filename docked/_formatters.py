from __future__ import annotations
import json
import shlex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._stage import Stage
    from ._types import BaseImage


def format_stage_name(stage: Stage | BaseImage | str) -> str:
    if isinstance(stage, str):
        return stage
    name = stage.name
    if name is None:
        raise ValueError('the stage must have a name to copy from it')
    return name


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
