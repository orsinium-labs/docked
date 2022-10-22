from __future__ import annotations
import json
from pathlib import PosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal
    from ._stage import Stage


class Instruction:
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


class FROM(Instruction):
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
            result += f' --digest={self.platform}'
        result += f' {self.image}'
        if self.tag:
            result += f':{self.tag}'
        if self.digest:
            result += f'@{self.digest}'
        if self.name:
            result += f' AS {self.name}'
        return result


class ARG(Instruction):
    """
    """
    __slots__ = ('name', 'default')

    def __init__(self, name: str, default: str | None = None) -> None:
        self.name = name
        self.default = default


class RUN(Instruction):
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
            result += ' ' + '&& \\\n    '.join((self.first,) + self.rest)
        else:
            result = ' ' + json.dumps(self.first)
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


class CMD(Instruction):
    """Provide defaults for an executing container.

    https://docs.docker.com/engine/reference/builder/#cmd
    """
    __slots__ = ('cmd', )

    def __init__(self, cmd: str | list[str]) -> None:
        self.cmd = cmd

    def as_str(self) -> str:
        result = 'CMD '
        if isinstance(self.cmd, str):
            result += self.cmd
        else:
            result = json.dumps(self.cmd)
        return result


class LABEL(Instruction):
    """Add metadata to an image

    https://docs.docker.com/engine/reference/builder/#label
    """
    __slots__ = ('name', 'default')

    def __init__(self, name: str, default: str | None = None) -> None:
        self.name = name
        self.default = default

    def as_str(self) -> str:
        result = f'LABEL {self.name}'
        default = self.default
        if default is not None:
            if not default or ' ' in default:
                default = f'"{default}"'
            default = default.replace('\n', '\\\n')
            result += f'={default}'
        return result


class EXPOSE(Instruction):
    """Inform Docker that the container listens on the specified network ports at runtime.

    The EXPOSE instruction does not actually publish the port.
    It functions as a type of documentation between the person who builds the image
    and the person who runs the container, about which ports are intended to be published.

    https://docs.docker.com/engine/reference/builder/#expose
    """
    __slots__ = ('port', 'protocol')

    def __init__(self, port: int, protocol: str = 'tcp') -> None:
        self.port = port
        self.protocol = protocol

    def as_str(self) -> str:
        return f'EXPOSE {self.port}/{self.protocol}'


class ENV(Instruction):
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
        if value is not None:
            if not value or ' ' in value:
                value = f'"{value}"'
            value = value.replace('\n', '\\\n')
            result += f'={value}'
        return result


class ADD(Instruction):
    """
    Copies new files, directories or remote file URLs from src and adds them
    to the filesystem of the image at the path dst.

    ADD is old, does too many things, and can suprise you by unpacking archives.
    If possible, use COPY instead. Or wget if you need to download remote files.

    https://docs.docker.com/engine/reference/builder/#add
    """
    __slots__ = ('src', 'dst', 'chown', 'checksum', 'keep_git_dir', 'link')

    def __init__(
        self,
        src: str | PosixPath | list[str | PosixPath],
        dst: str | PosixPath,
        *,
        chown: str | int | None = None,
        checksum: str | None = None,
        keep_git_dir: bool = False,
        link: bool = False,
    ) -> None:
        self.src = src
        self.dst = dst
        self.chown = chown
        self.checksum = checksum
        self.keep_git_dir = keep_git_dir
        self.link = link

    def as_str(self) -> str:
        result = 'ADD'
        if self.chown:
            result += f' --chown={self.chown}'
        if self.checksum:
            result += f' --checksum={self.checksum}'
        if self.keep_git_dir:
            result += ' --keep-git-dir=true'
        if self.link:
            result += ' --link'
        result += ' '
        parts = self._sources + [str(self.dst)]
        if any(' ' in part for part in parts):
            result += json.dumps(parts)
        else:
            result += ' '.join(parts)
        return result

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


class COPY(Instruction):
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
        result = 'ADD'
        if self.chown:
            result += f' --chown={self.chown}'
        if self.link:
            result += ' --link'
        from_name = self._from_name
        if from_name:
            result += f' --from={from_name}'
        result += ' '
        parts = self._sources + [str(self.dst)]
        if any(' ' in part for part in parts):
            result += json.dumps(parts)
        else:
            result += ' '.join(parts)
        return result

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
