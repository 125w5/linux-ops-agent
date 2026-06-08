from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalToolManifest:
    name: str
    command: str
    permission: str = "readonly"
    enabled: bool = False

    def validate(self) -> None:
        if self.permission != "readonly":
            raise ValueError("external tools must be readonly")
        if self.enabled:
            raise ValueError("external tools are disabled by default")
