from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING

from .._formatters import format_shell_cmd, json_if_spaces
from ._base import RunStep


if TYPE_CHECKING:
    from datetime import timedelta
    from signal import Signals
    from typing import Literal


class CMD(RunStep):
    """Provide defaults for an executing container.

    https://docs.docker.com/engine/reference/builder/#cmd
    """
    __slots__ = ('cmd', 'shell')

    def __init__(self, cmd: str | list[str], shell: bool = False) -> None:
        self.cmd = cmd
        self.shell = shell

    def as_str(self) -> str:
        return f'CMD {format_shell_cmd(self.cmd, shell=self.shell)}'


class EXPOSE(RunStep):
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


class ENTRYPOINT(RunStep):
    """Configure a container that will run as an executable.

    https://docs.docker.com/engine/reference/builder/#entrypoint
    """
    __slots__ = ('cmd', 'shell')

    def __init__(self, cmd: str | list[str], shell: bool = False) -> None:
        assert cmd
        self.cmd = cmd
        self.shell = shell

    def as_str(self) -> str:
        return f'ENTRYPOINT {format_shell_cmd(self.cmd, shell=self.shell)}'


class VOLUME(RunStep):
    """
    Create a mount point with the specified name and mark it as holding
    externally mounted volumes from native host or other containers.

    https://docs.docker.com/engine/reference/builder/#volume
    """
    __slots__ = ('paths', )

    def __init__(self, *paths: str | PosixPath) -> None:
        assert paths
        self.paths = paths

    def as_str(self) -> str:
        result = 'VOLUME'
        parts = [str(path) for path in self.paths]
        return f'{result} {json_if_spaces(parts)}'


class STOPSIGNAL(RunStep):
    """Sets the system call signal that will be sent to the container to exit.

    https://docs.docker.com/engine/reference/builder/#stopsignal
    """
    __slots__ = ('signal',)

    def __init__(self, signal: str | int | Signals) -> None:
        assert signal
        self.signal = signal

    def as_str(self) -> str:
        return f'STOPSIGNAL {self.signal}'


class HEALTHCHECK(RunStep):
    """Check container health by running a command inside the container.

    https://docs.docker.com/engine/reference/builder/#healthcheck
    """
    __slots__ = ('cmd', 'interval', 'timeout', 'start_period', 'retries', 'shell')

    def __init__(
        self,
        cmd: str | list[str] | None,
        *,
        interval: timedelta | str = '30s',
        timeout: timedelta | str = '30s',
        start_period: timedelta | str = '0s',
        retries: int = 3,
        shell: bool = False,
    ) -> None:
        assert cmd or cmd is None
        self.cmd = cmd
        self.interval = interval
        self.timeout = timeout
        self.start_period = start_period
        self.retries = retries
        self.shell = shell

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
            result += f' CMD {format_shell_cmd(self.cmd, shell=self.shell)}'
        return result

    @staticmethod
    def _convert_duration(td: timedelta | str) -> str:
        if isinstance(td, str):
            return td
        return f'{td.seconds}s'
