from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandProfile:
    command: str
    help_text: str
    man_text: str
    flags: list[str] = field(default_factory=list)
    likely_readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "help_text": self.help_text,
            "man_text": self.man_text,
            "flags": self.flags,
            "likely_readonly": self.likely_readonly,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandProfile":
        return cls(
            command=str(data["command"]),
            help_text=str(data.get("help_text", "")),
            man_text=str(data.get("man_text", "")),
            flags=list(data.get("flags", [])),
            likely_readonly=bool(data.get("likely_readonly", True)),
        )


def extract_flags(text: str) -> list[str]:
    flags = sorted(set(re.findall(r"(?<!\w)(--?[A-Za-z][A-Za-z0-9-]*)", text)))
    return flags[:80]
