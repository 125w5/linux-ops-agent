from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FocusRing:
    panes: list[str]
    index: int = 0

    @property
    def active(self) -> str:
        if not self.panes:
            return ""
        return self.panes[self.index % len(self.panes)]

    def next(self) -> str:
        if self.panes:
            self.index = (self.index + 1) % len(self.panes)
        return self.active

    def previous(self) -> str:
        if self.panes:
            self.index = (self.index - 1) % len(self.panes)
        return self.active
