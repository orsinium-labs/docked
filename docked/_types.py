from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal


class Checksum:
    """Hash of remote content for DOWNLOAD.
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
