from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Container, Iterator, TextIO, overload

from ._linter import lint


if TYPE_CHECKING:
    from ._stage import Stage


DEFAULT_CHANNEL = 'docker/dockerfile'


class Image:
    """A Docker image. Consists of one or more Stages.

    Args:
        *stages: at least one stage. Multiple for multi-stage builds.
        syntax_channel: the Dockerfile syntax to use. Default: ``docker/dockerfile``.
        syntax_version: the Dockerfile syntax version to use.
            If not specified explicitly, will be detected based on the features
            you use, sticking to the lowest minor version possible.
        escape: the escape character to use in Dockerfile. Default: ``\\``.
    """
    __slots__ = ('stages', 'syntax_channel', 'syntax_version', 'escape')

    def __init__(
        self,
        first: Stage, *rest: Stage,
        syntax_channel: str = DEFAULT_CHANNEL,
        syntax_version: str | None = None,
        escape: str = '\\',
    ) -> None:
        if syntax_channel != DEFAULT_CHANNEL and not syntax_version:
            raise ValueError('syntax_version is required with non-default syntax_channel')
        self.stages = (first,) + rest
        self.syntax_channel = syntax_channel
        self.syntax_version = syntax_version
        self.escape = escape

    @property
    def min_version(self) -> str:
        """The minimal Dockerfile version required.

        Determined based on the instructions and their arguments used.
        """
        versions = (stage.min_version for stage in self.stages)
        return max(versions, default='1.0')

    @property
    def syntax(self) -> str:
        """Syntax of the Dockerfile to use.

        If no ``syntax_version`` provided, the ``min_version`` will be used.
        """
        version = self.syntax_version or self.min_version
        return f'{self.syntax_channel}:{version}'

    def as_str(self) -> str:
        """Generate Dockerfile.
        """
        return '\n'.join(self.iter_lines())

    def iter_lines(self) -> Iterator[str]:
        """Iterate over lines of Dockerfile.

        Useful for writing a big Dockerfile in a file or a stream.
        """
        yield f'# syntax={self.syntax}'
        yield f'# escape={self.escape}'
        for stage in self.stages:
            yield ''
            yield from stage.iter_lines()

    @overload
    def save(self, path: Path) -> None:
        pass

    @overload
    def save(self, path: None = None) -> Path:
        pass

    def save(self, path: Path | None = None) -> Path | None:
        """Save Dockerfile in the given file path.

        If no path provided, save into a temporary file and return the file path.
        """
        result = None
        if path is None:
            tmp_path = NamedTemporaryFile(delete=False)
            path = Path(tmp_path.name)
            result = path
        with path.open('w', encoding='utf8') as stream:
            for line in self.iter_lines():
                print(line, file=stream)
        return result

    def build(
        self,
        args: list[str] | None = None,
        binary: str = 'docker',
        exit_on_failure: bool = True,
        stdout: TextIO = sys.stdout,
        stderr: TextIO = sys.stderr,
    ) -> int:
        """Build the image using syscalls to the Docker CLI.

        Args:
            args: additional CLI arguments to pass into Docker binary.
            binary: docker binary to use. Must be either a path or in $PATH.
            exit_on_failure: set to False to make the method return the exit code
                as a result instead of calling ``sys.exit`` on failure.
            stdout: stream to pipe Docker CLI stdout into.
            stderr: stream to pipe Docker CLI stderr into.
        """
        if args is None:
            args = sys.argv[1:]
        with NamedTemporaryFile(mode='w+') as tmp_path:
            for line in self.iter_lines():
                print(line, file=tmp_path)
            tmp_path.flush()
            cmd = [binary, 'buildx', 'build', '-f', tmp_path.name, *args]
            result = subprocess.run(cmd, stdout=stdout, stderr=stderr)
        if exit_on_failure and result.returncode != 0:
            sys.exit(result.returncode)
        return result.returncode

    def lint(
        self,
        disable_codes: Container[int] = (),
        stdout: TextIO = sys.stdout,
        exit_on_failure: bool = True,
    ) -> int:
        """Run linter on the image.

        Args:
            disable_codes: error codes to skip. Leave it empty by default,
                add some values into it when you face false-positives.
            stdout: stream where to write the reported violations.
            exit_on_failure: set to False to return exit code on failure
                instead of callin ``sys.exit``.
        """
        count = 0
        for v in lint(self):
            if v.code in disable_codes:
                continue
            print(v, file=stdout)
            count += 1
        if exit_on_failure and count:
            sys.exit(min(count, 100))
        return count

    def __str__(self) -> str:
        return self.as_str()
