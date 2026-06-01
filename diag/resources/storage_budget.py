from __future__ import annotations


def within_storage_budget(size_bytes: int, max_bytes: int) -> bool:
    return size_bytes <= max_bytes
