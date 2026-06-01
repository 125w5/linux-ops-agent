from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    text: str
    truncated: bool = False
    offset: int = 0
    limit: int = 0


def tail_lines(lines: list[str], limit: int = 200) -> Page:
    if len(lines) <= limit:
        return Page("\n".join(lines), False, 0, limit)
    return Page("\n".join(lines[-limit:]), True, len(lines) - limit, limit)


def preview_bytes(text: str, max_bytes: int = 100 * 1024) -> Page:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return Page(text, False, 0, max_bytes)
    clipped = encoded[:max_bytes].decode("utf-8", errors="ignore")
    return Page(clipped + "\n[truncated]", True, 0, max_bytes)


def page_lines(lines: list[str], page: int = 0, page_size: int = 50) -> Page:
    start = max(0, page) * page_size
    end = start + page_size
    selected = lines[start:end]
    return Page("\n".join(selected), end < len(lines), start, page_size)
