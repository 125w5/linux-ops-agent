from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScrollState:
    offsets: dict[str, int] = field(default_factory=dict)

    def get(self, pane: str) -> int:
        return self.offsets.get(pane, 0)

    def move(self, pane: str, delta: int, maximum: int = 0) -> int:
        current = self.offsets.get(pane, 0)
        next_value = max(0, current + delta)
        if maximum > 0:
            next_value = min(next_value, maximum)
        self.offsets[pane] = next_value
        return next_value

    def page_down(self, pane: str, page_size: int = 20, maximum: int = 0) -> int:
        return self.move(pane, page_size, maximum)

    def page_up(self, pane: str, page_size: int = 20) -> int:
        return self.move(pane, -page_size)
