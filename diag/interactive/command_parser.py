from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedInput:
    is_command: bool
    name: str
    args: str = ""


def parse_interactive_input(text: str) -> ParsedInput:
    stripped = text.strip()
    if not stripped.startswith("/"):
        return ParsedInput(False, "", stripped)
    name, _, args = stripped.partition(" ")
    return ParsedInput(True, name.lower(), args.strip())
