from __future__ import annotations


def stage_line(index: int, total: int, message: str) -> str:
    return f"[{index}/{total}] {message}"
