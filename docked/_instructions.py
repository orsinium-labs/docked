from __future__ import annotations


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
            raise ValueError("can't set both tag and digest")
        self.image = image
        self.tag = tag
        self.digest = digest
        self.platform = platform
        self.name = name

    def as_str(self) -> str:
        return super().as_str()


class ARG(Instruction):
    __slots__ = ('name', 'default')

    def __init__(self, name: str, default: str | None = None) -> None:
        self.name = name
        self.default = default
