from __future__ import annotations


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


def within_token_budget(text: str, max_tokens: int) -> bool:
    return estimate_tokens(text) <= max_tokens


def fit_text_to_token_budget(text: str, max_tokens: int) -> tuple[str, bool]:
    if within_token_budget(text, max_tokens):
        return text, False
    max_chars = max(0, max_tokens * 4)
    marker = "\n[truncated: AI input budget exceeded]"
    if max_chars <= len(marker):
        return marker.strip(), True
    return text[: max_chars - len(marker)].rstrip() + marker, True
