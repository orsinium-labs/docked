from __future__ import annotations

from dataclasses import dataclass, replace
import logging


@dataclass(frozen=True)
class Violation:
    code: int
    severity: int
    summary: str

    @property
    def severity_text(self) -> str:
        return logging.getLevelName(self.severity)

    def format(self, **kwargs) -> Violation:
        return replace(self, summary=self.summary.format(**kwargs))

    def __str__(self) -> str:
        return f'{self.severity_text[0]}{self.code:03}: {self.summary}'
