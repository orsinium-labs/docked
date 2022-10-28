from __future__ import annotations

import logging
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Violation:
    """

    Severity:
        ERROR:      never do that.
        WARNING:    don't do that unless you're 100% sure.
        INFO:       it's strange you do that but ok, just checking.
    """
    code: int
    severity: int
    summary: str
    url: str | None = None

    @property
    def severity_text(self) -> str:
        return logging.getLevelName(self.severity)

    def format(self, **kwargs: str) -> Violation:
        return replace(self, summary=self.summary.format(**kwargs))

    def __str__(self) -> str:
        return f'{self.severity_text[0]}{self.code:04}: {self.summary}'
