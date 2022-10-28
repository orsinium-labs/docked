"""
A human-friendly alternative to Dockerfile.

It's a Python library for generating Docker images,
with API designed to be safe, secure, and easy-to-use correctly.
"""

from . import cmd
from ._stage import Stage
from ._image import Image
from ._types import Checksum, Mount, BindMount, CacheMount, SecretMount, SSHMount, BaseImage
from ._steps import (
    Step,
    ARG,
    RUN,
    CMD,
    EXPOSE,
    ENV,
    DOWNLOAD, EXTRACT, CLONE,
    COPY,
    ENTRYPOINT,
    VOLUME,
    USER,
    WORKDIR,
    ONBUILD,
    STOPSIGNAL,
    HEALTHCHECK,
    SHELL,
)

__version__ = '0.1.0'
__all__ = [
    # classes and things
    'BaseImage',
    'BindMount',
    'CacheMount',
    'Checksum',
    'cmd',
    'Image',
    'Mount',
    'SecretMount',
    'SSHMount',
    'Stage',
    'Step',

    # steps
    'ARG',
    'CLONE',
    'CMD',
    'COPY',
    'DOWNLOAD',
    'ENTRYPOINT',
    'ENV',
    'EXPOSE',
    'EXTRACT',
    'HEALTHCHECK',
    'ONBUILD',
    'RUN',
    'SHELL',
    'STOPSIGNAL',
    'USER',
    'VOLUME',
    'WORKDIR',
]
