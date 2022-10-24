from __future__ import annotations

import json
from pathlib import PosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import timedelta
    from signal import Signals
    from typing import Literal

    from ._stage import Stage


def _maybe_list(val: str | list[str]) -> str:
    if isinstance(val, str):
        return val
    return json.dumps(val)


def json_if_spaces(vals: list[str]) -> str:
    if any(' ' in val for val in vals):
        return json.dumps(vals)
    return ' '.join(vals)


class Step:
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


class FROM(Step):
    """Initializes a new build stage and sets the Base Image for subsequent instructions.

    https://docs.docker.com/engine/reference/builder/#from
    """
    __slots__ = ('image', 'tag', 'digest', 'platform', 'name')

    def __init__(
        self,
        image: str,
        tag: str | None = None,
        *,
        digest: str | None = None,
        platform: str | None = None,
        name: str | None = None,
    ) -> None:
        if tag and digest:
            raise ValueError('cannot set both tag and digest')
        self.image = image
        self.tag = tag
        self.digest = digest
        self.platform = platform
        self.name = name

    def as_str(self) -> str:
        result = 'FROM'
        if self.platform:
            result += f' --platform={self.platform}'
        result += f' {self.image}'
        if self.tag:
            result += f':{self.tag}'
        if self.digest:
            result += f'@{self.digest}'
        if self.name:
            result += f' AS {self.name}'
        return result


class ARG(Step):
    """
    Define a variable that users can pass at build-time to the builder with the `docker build`.

    The difference with ENV is that env vars set with ARG
    are not available in running container, only at build-time.

    https://docs.docker.com/engine/reference/builder/#arg
    """
    __slots__ = ('name', 'default')

    def __init__(self, name: str, default: str | None = None) -> None:
        self.name = name
        self.default = default

    def as_str(self) -> str:
        result = f'ARG {self.name}'
        if self.default is not None:
            result += f'={self.default}'
        return result


class RUN(Step):
    """Execute any commands in a new layer on top of the current image and commit the results.

    https://docs.docker.com/engine/reference/builder/#run
    """
    __slots__ = ('first', 'rest', 'mount', 'network', 'security')

    def __init__(
        self,
        first: str | list[str],
        *rest: str,
        mount: Literal['bind', 'cache', 'tmpfs', 'secret', 'ssh'] = 'bind',
        network: Literal['default', 'none', 'host'] = 'default',
        security: Literal['insecure', 'sandbox'] = 'sandbox',
    ) -> None:
        if not isinstance(first, str) and rest:
            raise ValueError('cannot use list ("exec form") with multiple commands')
        self.first = first
        self.rest = rest
        self.mount = mount
        self.network = network
        self.security = security

    def as_str(self) -> str:
        result = 'RUN'
        if self.mount != 'bind':
            result += f' --mount={self.mount}'
        if self.network != 'default':
            result += f' --network={self.network}'
        if self.security != 'sandbox':
            result += f' --security={self.security}'
        if isinstance(self.first, str):
            result += ' ' + ' && \\\n    '.join((self.first,) + self.rest)
        else:
            result += ' ' + json.dumps(self.first)
        return result

    @property
    def min_version(self) -> str:
        if self.security != 'sandbox':
            return 'labs'
        if self.mount != 'bind':
            return '1.2'
        if self.network != 'default':
            return '1.1'
        return '1.0'


class CMD(Step):
    """Provide defaults for an executing container.

    https://docs.docker.com/engine/reference/builder/#cmd
    """
    __slots__ = ('cmd', )

    def __init__(self, cmd: str | list[str]) -> None:
        self.cmd = cmd

    def as_str(self) -> str:
        return f'CMD {_maybe_list(self.cmd)}'


class LABEL(Step):
    """Add metadata to an image

    https://docs.docker.com/engine/reference/builder/#label
    """
    __slots__ = ('name', 'value')

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def as_str(self) -> str:
        result = f'LABEL {self.name}'
        value = self.value
        if not value or ' ' in value:
            value = f'"{value}"'
        result += f'={value}'
        return result


class EXPOSE(Step):
    """Inform Docker that the container listens on the specified network ports at runtime.

    The EXPOSE instruction does not actually publish the port.
    It functions as a type of documentation between the person who builds the image
    and the person who runs the container, about which ports are intended to be published.

    https://docs.docker.com/engine/reference/builder/#expose
    """
    __slots__ = ('port', 'protocol')

    def __init__(self, port: int, protocol: Literal['tcp', 'udp'] = 'tcp') -> None:
        self.port = port
        self.protocol = protocol

    def as_str(self) -> str:
        return f'EXPOSE {self.port}/{self.protocol}'


class ENV(Step):
    """Set an environment variable.

    The environment variables set using ENV will persist when a container
    is run from the resulting image.

    https://docs.docker.com/engine/reference/builder/#env
    """
    __slots__ = ('key', 'value')

    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value

    def as_str(self) -> str:
        result = f'ENV {self.key}'
        value = self.value
        if not value or ' ' in value:
            value = f'"{value}"'
        result += f'={value}'
        return result


class ADD(Step):
    """
    Copies new files, directories or remote file URLs from src and adds them
    to the filesystem of the image at the path dst.

    ADD is old, does too many things, and can suprise you by unpacking archives.
    If possible, use COPY instead. Or wget if you need to download remote files.

    https://docs.docker.com/engine/reference/builder/#add
    """
    __slots__ = ('src', 'dst', 'chown', 'checksum', 'keep_git_dir', 'link', 'checksum_algoritm')

    def __init__(
        self,
        src: str | PosixPath | list[str | PosixPath],
        dst: str | PosixPath,
        *,
        chown: str | int | None = None,
        checksum_algoritm: Literal['sha256', 'sha384', 'sha512', 'blake3'] = 'sha256',
        checksum: str | None = None,
        keep_git_dir: bool = False,
        link: bool = False,
    ) -> None:
        self.src = src
        self.dst = dst
        self.chown = chown
        self.checksum = checksum
        self.keep_git_dir = keep_git_dir
        self.checksum_algoritm = checksum_algoritm
        self.link = link

    def as_str(self) -> str:
        result = 'ADD'
        if self.chown:
            result += f' --chown={self.chown}'
        if self.checksum:
            result += f' --checksum={self.checksum_algoritm}:{self.checksum}'
        if self.keep_git_dir:
            result += ' --keep-git-dir=true'
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
        if self.checksum or self.keep_git_dir:
            return 'labs'
        if isinstance(self.src, str) and self.src.startswith('git@'):
            return 'labs'
        if self.link:
            return '1.4'
        return '1.0'


class COPY(Step):
    """
    Copies new files or directories from src and adds them to the filesystem
    of the container at the path dst.

    The difference with ADD is that COPY:

    1. Can't download files from URL or git.
    2. Doesn't unpack archives.
    3. Can copy files from previous stages.

    https://docs.docker.com/engine/reference/builder/#copy
    """
    __slots__ = ('src', 'dst', 'chown', 'link', 'from_stage')

    def __init__(
        self,
        src: str | PosixPath | list[str | PosixPath],
        dst: str | PosixPath,
        *,
        from_stage: Stage | str | None = None,
        chown: str | int | None = None,
        link: bool = False,
    ) -> None:
        self.src = src
        self.dst = dst
        self.from_stage = from_stage
        self.chown = chown
        self.link = link

    def as_str(self) -> str:
        result = 'COPY'
        if self.chown:
            result += f' --chown={self.chown}'
        if self.link:
            result += ' --link'
        from_name = self._from_name
        if from_name:
            result += f' --from={from_name}'
        parts = self._sources + [str(self.dst)]
        return f'{result} {json_if_spaces(parts)}'

    @property
    def _sources(self) -> list[str]:
        if isinstance(self.src, list):
            return [str(s) for s in self.src]
        return [str(self.src)]

    @property
    def _from_name(self) -> str | None:
        if self.from_stage is None:
            return None
        if isinstance(self.from_stage, str):
            return self.from_stage
        name = self.from_stage.name
        if name is None:
            raise ValueError('the stage must have a name to copy from it')
        return name

    @property
    def min_version(self) -> str:
        if self.link:
            return '1.4'
        return '1.0'


class ENTRYPOINT(Step):
    """Configure a container that will run as an executable.

    https://docs.docker.com/engine/reference/builder/#entrypoint
    """
    __slots__ = ('cmd',)

    def __init__(self, cmd: str | list[str]) -> None:
        self.cmd = cmd

    def as_str(self) -> str:
        return f'ENTRYPOINT {_maybe_list(self.cmd)}'


class VOLUME(Step):
    """
    Create a mount point with the specified name and mark it as holding
    externally mounted volumes from native host or other containers.

    https://docs.docker.com/engine/reference/builder/#volume
    """
    __slots__ = ('paths', )

    def __init__(self, *paths: str | PosixPath) -> None:
        self.paths = paths

    def as_str(self) -> str:
        result = 'VOLUME'
        parts = [str(path) for path in self.paths]
        return f'{result} {json_if_spaces(parts)}'


class USER(Step):
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


class WORKDIR(Step):
    """
    Set the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow.

    If the path doesn't exist, it will be created.

    https://docs.docker.com/engine/reference/builder/#workdir
    """
    __slots__ = ('path', )

    def __init__(self, path: str | PosixPath) -> None:
        self.path = path

    def as_str(self) -> str:
        return f'WORKDIR {self.path}'


class ONBUILD(Step):
    """
    Add to the image a trigger instruction to be executed at a later time,
    when the image is used as the base for another build.

    https://docs.docker.com/engine/reference/builder/#onbuild
    """
    __slots__ = ('trigger',)

    def __init__(self, trigger: Step) -> None:
        if isinstance(trigger, ONBUILD):
            raise ValueError('cannot use ONBUILD inside ONBUILD')
        self.trigger = trigger

    def as_str(self) -> str:
        return f'ONBUILD {self.trigger.as_str()}'


class STOPSIGNAL(Step):
    """Sets the system call signal that will be sent to the container to exit.

    https://docs.docker.com/engine/reference/builder/#stopsignal
    """
    __slots__ = ('signal',)

    def __init__(self, signal: str | int | Signals) -> None:
        self.signal = signal

    def as_str(self) -> str:
        return f'STOPSIGNAL {self.signal}'


class HEALTHCHECK(Step):
    """Check container health by running a command inside the container.

    https://docs.docker.com/engine/reference/builder/#healthcheck
    """
    __slots__ = ('cmd', 'interval', 'timeout', 'start_period', 'retries')

    def __init__(
        self,
        cmd: str | list[str] | None,
        *,
        interval: timedelta | str = '30s',
        timeout: timedelta | str = '30s',
        start_period: timedelta | str = '0s',
        retries: int = 3,
    ) -> None:
        self.cmd = cmd
        self.interval = interval
        self.timeout = timeout
        self.start_period = start_period
        self.retries = retries

    def as_str(self) -> str:
        result = 'HEALTHCHECK'
        if self.interval != '30s':
            result += f' --interval={self._convert_duration(self.interval)}'
        if self.timeout != '30s':
            result += f' --timeout={self._convert_duration(self.timeout)}'
        if self.start_period != '0s':
            result += f' --start-period={self._convert_duration(self.start_period)}'
        if self.retries != 3:
            result += f' --retries={self.retries}'
        if self.cmd is None:
            result += ' NONE'
        else:
            result += f' CMD {_maybe_list(self.cmd)}'
        return result

    @staticmethod
    def _convert_duration(td: timedelta | str) -> str:
        if isinstance(td, str):
            return td
        return f'{td.seconds}s'


class SHELL(Step):
    """Override the default shell used for the shell form of commands.

    It affects shell form commands inside of RUN, CMD, and ENTRYPOINT instructions.

    https://docs.docker.com/engine/reference/builder/#shell
    """
    __slots__ = ('cmd', )

    def __init__(self, cmd: list[str]) -> None:
        self.cmd = cmd

    def as_str(self) -> str:
        return f'SHELL {json.dumps(self.cmd)}'
