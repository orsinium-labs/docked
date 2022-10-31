from __future__ import annotations

from dataclasses import dataclass
from pathlib import PosixPath
from typing import TYPE_CHECKING

from ._formatters import format_stage_name


if TYPE_CHECKING:
    from typing import Literal

    from ._stage import Stage


class BaseImage:
    """Type representing a base image, like the ones you can find on Docker Hub.

    It's used in Stage to specify ``FROM``, in COPY to specify ``--from``
    and in some ``--mount`` types in ``RUN``.

    Args:
        name: image name. For example, "python".
        tag: image tag. For example, "3.11-alpine".
        digest: the layer has of the image to use. You can find it on Docker Hub.
            Can't be used together with ``tag``, pick one.
    """
    __slots__ = ('name', 'tag', 'digest')

    def __init__(
        self,
        name: str,
        tag: str | None = None,
        digest: str | None = None,
    ) -> None:
        assert not tag or not digest, 'cannot set digest and tag at the same time'
        self.name = name
        self.tag = tag
        self.digest = digest

    def __str__(self) -> str:
        if self.tag:
            return f'{self.name}:{self.tag}'
        if self.digest:
            return f'{self.name}@{self.digest}'
        return self.name


class Checksum:
    """Hash of remote content for DOWNLOAD.

    Args:
        hex: base 16 representation of the hash value.
        algorithm: the name of algorithm used to obtain the hash.
    """
    __slots__ = ('hex', 'algorithm')

    def __init__(
        self,
        hex: str,
        *,
        algorithm: Literal['sha256', 'sha384', 'sha512', 'blake3'] = 'sha256',
    ) -> None:
        self.hex = hex
        self.algorithm = algorithm

    def __str__(self) -> str:
        return f'{self.algorithm}:{self.hex}'


class Mount:
    """Create a mount that process running as part of the build can access.

    This can be used to bind files from other part of the build without copying,
    accessing build secrets or ssh-agent sockets,
    or creating cache locations to speed up your build.
    """
    __slots__ = ()

    @property
    def _parts(self) -> list[tuple[str, str]]:
        raise NotImplementedError

    def __str__(self) -> str:
        return ','.join(f'{k}={v}' for k, v in self._parts)


@dataclass
class BindMount(Mount):
    """Allows binding directories (read-only) in the context or in an image.

    Args:
        target: Mount path.
        source: Source path in the from_stage. Defaults to the root of the from.
        from_stage: Stage or BaseImage for the root of the source. Defaults to the build context.
        allow_write: Allow writes on the mount. Written data will be discarded.

    https://docs.docker.com/engine/reference/builder/#run---mounttypebind
    """
    target: str | PosixPath
    source: str | PosixPath | None = None
    from_stage: Stage | BaseImage | None = None
    allow_write: bool = False

    @property
    def _parts(self) -> list[tuple[str, str]]:
        parts = [
            ('type', 'bind'),
            ('target', str(self.target)),
        ]
        if self.source:
            parts.append(('source', str(self.source)))
        if self.from_stage:
            parts.append(('from', format_stage_name(self.from_stage)))
        if self.allow_write:
            parts.append(('rw', 'true'))
        return parts


@dataclass
class CacheMount(Mount):
    """Allows to cache directories for compilers and package managers.

    https://docs.docker.com/engine/reference/builder/#run---mounttypecache
    """
    target: str | PosixPath
    id: str | None = None
    allow_write: bool = True
    sharing: Literal['shared', 'private', 'locked'] = 'shared'
    from_stage: Stage | BaseImage | None = None
    source: str | PosixPath | None = None
    mode: int = 0o755
    uid: int = 0
    gid: int = 0

    @property
    def _parts(self) -> list[tuple[str, str]]:
        parts = [
            ('type', 'cache'),
            ('target', str(self.target)),
        ]
        if self.id:
            parts.append(('id', self.id))
        if not self.allow_write:
            parts.append(('ro', 'true'))
        if self.sharing != 'shared':
            parts.append(('sharing', self.sharing))
        if self.from_stage:
            parts.append(('from', format_stage_name(self.from_stage)))
        if self.source:
            parts.append(('source', str(self.source)))
        if self.mode != 0o755:
            parts.append(('mode', oct(self.mode).replace('o', '')))
        if self.uid:
            parts.append(('uid', str(self.uid)))
        if self.gid:
            parts.append(('gid', str(self.gid)))
        return parts


@dataclass
class TmpFSMount(Mount):
    """Allows mounting tmpfs in the build container.

    https://docs.docker.com/engine/reference/builder/#run---mounttypetmpfs
    """
    target: str | PosixPath
    size: str | None = None

    @property
    def _parts(self) -> list[tuple[str, str]]:
        parts = [
            ('type', 'tmpfs'),
            ('target', str(self.target)),
        ]
        if self.size:
            parts.append(('size', self.size))
        return parts


@dataclass
class SecretMount(Mount):
    """Allows to access secure files such as private keys without baking them into the image.

    https://docs.docker.com/engine/reference/builder/#run---mounttypesecret
    """
    target: str | PosixPath | None = None
    id: str | None = None
    required: bool = False
    mode: int = 0o400
    uid: int = 0
    gid: int = 0

    @property
    def _parts(self) -> list[tuple[str, str]]:
        parts = [('type', 'secret')]
        if self.target:
            parts.append(('target', str(self.target)))
        if self.id:
            parts.append(('id', self.id))
        if self.required:
            parts.append(('required', 'true'))
        if self.mode != 0o400:
            parts.append(('mode', oct(self.mode).replace('o', '')))
        if self.uid:
            parts.append(('uid', str(self.uid)))
        if self.gid:
            parts.append(('gid', str(self.gid)))
        return parts


@dataclass
class SSHMount(Mount):
    """Allows to access SSH keys via SSH agents, with support for passphrases.

    https://docs.docker.com/engine/reference/builder/#run---mounttypessh
    """
    target: str | PosixPath | None = None
    id: str = 'default'
    required: bool = False
    mode: int = 0o600
    uid: int = 0
    gid: int = 0

    @property
    def _parts(self) -> list[tuple[str, str]]:
        parts = [('type', 'ssh')]
        if self.target:
            parts.append(('target', str(self.target)))
        if self.id != 'default':
            parts.append(('id', self.id))
        if self.required:
            parts.append(('required', 'true'))
        if self.mode != 0o600:
            parts.append(('mode', oct(self.mode).replace('o', '')))
        if self.uid:
            parts.append(('uid', str(self.uid)))
        if self.gid:
            parts.append(('gid', str(self.gid)))
        return parts
