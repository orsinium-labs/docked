from __future__ import annotations

from dataclasses import dataclass
from pathlib import PosixPath
from typing import TYPE_CHECKING

from .._formatters import format_shell_cmd, format_stage_name, json_if_spaces
from ._base import BuildStep


if TYPE_CHECKING:
    from typing import Literal

    from .._stage import Stage
    from .._types import BaseImage, Checksum, Mount


class ARG(BuildStep):
    """
    Define a variable that users can pass at build-time to the builder with the `docker build`.

    The difference with ENV is that env vars set with ARG
    are not available in running container, only at build-time.

    https://docs.docker.com/engine/reference/builder/#arg
    """
    __slots__ = ('name', 'default')

    def __init__(self, name: str, default: str | None = None) -> None:
        assert name
        self.name = name
        self.default = default

    def as_str(self) -> str:
        result = f'ARG {self.name}'
        if self.default is not None:
            result += f'={self.default}'
        return result


class RUN(BuildStep):
    """Execute any commands in a new layer on top of the current image and commit the results.

    https://docs.docker.com/engine/reference/builder/#run
    """
    __slots__ = ('first', 'rest', 'mount', 'network', 'security', 'shell')

    def __init__(
        self,
        first: str | list[str],
        *rest: str,
        mount: Mount | None = None,
        network: Literal['default', 'none', 'host'] = 'default',
        security: Literal['insecure', 'sandbox'] = 'sandbox',
        shell: bool = True,
    ) -> None:
        assert first
        if not shell and rest:
            raise ValueError('cannot use `shell=False` with multiple commands')
        self.first = first
        self.rest = rest
        self.mount = mount
        self.network = network
        self.security = security
        self.shell = shell

    def as_str(self) -> str:
        result = 'RUN'
        if self.mount is not None:
            result += f' --mount={self.mount}'
        if self.network != 'default':
            result += f' --network={self.network}'
        if self.security != 'sandbox':
            result += f' --security={self.security}'
        if isinstance(self.first, str) and self.rest:
            result += ' ' + ' && \\\n    '.join((self.first,) + self.rest)
        else:
            result += ' ' + format_shell_cmd(self.first, shell=self.shell)
        return result

    @property
    def min_version(self) -> str:
        if self.security != 'sandbox':
            return 'labs'
        if self.mount is not None:
            return '1.2'
        if self.network != 'default':
            return '1.1'
        return '1.0'


class ENV(BuildStep):
    """Set an environment variable.

    The environment variables set using ENV will persist when a container
    is run from the resulting image.

    https://docs.docker.com/engine/reference/builder/#env
    """
    __slots__ = ('key', 'value')

    def __init__(self, key: str, value: str) -> None:
        assert key
        self.key = key
        self.value = value

    def as_str(self) -> str:
        result = f'ENV {self.key}'
        value = self.value
        if not value or ' ' in value:
            value = f'"{value}"'
        result += f'={value}'
        return result


@dataclass(repr=False)
class _BaseAdd(BuildStep):
    src: str | PosixPath | list[str | PosixPath]
    dst: str | PosixPath
    chown: str | int | None = None
    link: bool = False

    def as_str(self) -> str:
        result = ''
        if self.chown:
            result += f' --chown={self.chown}'
        if self.link:
            result += ' --link'
        parts = self._sources + [str(self.dst)]
        return f'{result} {json_if_spaces(parts)}'

    @property
    def _sources(self) -> list[str]:
        if isinstance(self.src, list):
            return [str(s) for s in self.src]
        return [str(self.src)]

    @property
    def min_version(self) -> str:
        if self.link:
            return '1.4'
        return '1.0'


@dataclass
class DOWNLOAD(_BaseAdd):
    """Download a remote file.

    https://docs.docker.com/engine/reference/builder/#add
    """
    checksum: Checksum | None = None

    def as_str(self) -> str:
        result = 'ADD'
        if self.checksum:
            result += f' --checksum={self.checksum}'
        return f'{result}{super().as_str()}'

    @property
    def min_version(self) -> str:
        if self.checksum:
            return 'master-labs'
        return super().min_version


@dataclass
class CLONE(_BaseAdd):
    """Clone a git repository.

    Currently, available only in development channel. So, you'll need to explicitly
    specify the syntax to use this instruction::

        image = d.Image(
            stage,
            syntax_channel='docker/dockerfile-upstream',
        )

    https://docs.docker.com/engine/reference/builder/#adding-a-git-repository-add-git-ref-dir
    """
    keep_git_dir: bool = False

    def as_str(self) -> str:
        result = 'ADD'
        if self.keep_git_dir:
            result += ' --keep-git-dir=true'
        return f'{result}{super().as_str()}'

    @property
    def min_version(self) -> str:
        return 'master-labs'


class EXTRACT(_BaseAdd):
    """Extract an archive from the host machine into the image.

    Supported formats: identity, gzip, bzip2, and xz.

    https://docs.docker.com/engine/reference/builder/#add
    """

    def as_str(self) -> str:
        return f'ADD{super().as_str()}'


@dataclass
class COPY(_BaseAdd):
    """
    Copies new files or directories from src and adds them to the filesystem
    of the image at the path dst.

    https://docs.docker.com/engine/reference/builder/#copy
    """
    from_stage: Stage | BaseImage | None = None

    def as_str(self) -> str:
        result = 'COPY'
        if self.from_stage:
            result += f' --from={format_stage_name(self.from_stage)}'
        return f'{result}{super().as_str()}'


class USER(BuildStep):
    """Set the user name to use as the default user for the remainder of the stage.

    https://docs.docker.com/engine/reference/builder/#user
    """
    __slots__ = ('user', 'group')

    def __init__(self, user: str | int, group: str | int | None = None) -> None:
        self.user = user
        self.group = group

    def as_str(self) -> str:
        result = f'USER {self.user}'
        if self.group is not None:
            result += f':{self.group}'
        return result


class WORKDIR(BuildStep):
    """
    Set the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow.

    If the path doesn't exist, it will be created.

    https://docs.docker.com/engine/reference/builder/#workdir
    """
    __slots__ = ('path', )

    def __init__(self, path: str | PosixPath) -> None:
        assert path
        self.path = path

    def as_str(self) -> str:
        return f'WORKDIR {self.path}'


class ONBUILD(BuildStep):
    """
    Add to the image a trigger instruction to be executed at a later time,
    when the image is used as the base for another build.

    https://docs.docker.com/engine/reference/builder/#onbuild
    """
    __slots__ = ('trigger',)

    def __init__(self, trigger: BuildStep) -> None:
        assert not isinstance(trigger, ONBUILD), 'cannot use ONBUILD inside ONBUILD'
        self.trigger = trigger

    def as_str(self) -> str:
        return f'ONBUILD {self.trigger.as_str()}'


class SHELL(BuildStep):
    """Override the default shell used for the shell form of commands.

    It affects shell form commands inside of RUN, CMD, and ENTRYPOINT instructions.

    https://docs.docker.com/engine/reference/builder/#shell
    """
    __slots__ = ('cmd', )

    def __init__(self, cmd: str | list[str]) -> None:
        assert cmd
        self.cmd = cmd

    def as_str(self) -> str:
        return f'SHELL {format_shell_cmd(self.cmd, shell=False)}'
