from __future__ import annotations

import json
from pathlib import Path

from diag.tooldocs.command_profile import CommandProfile
from diag.utils.paths import project_root


def default_doc_store_path() -> Path:
    return project_root() / "outputs" / "history" / "tooldocs.json"


class ToolDocStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_doc_store_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, CommandProfile]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {name: CommandProfile.from_dict(item) for name, item in data.items()}

    def save(self, profiles: dict[str, CommandProfile]) -> None:
        self.path.write_text(
            json.dumps({name: profile.to_dict() for name, profile in profiles.items()}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def put(self, profile: CommandProfile) -> None:
        profiles = self.load()
        profiles[profile.command] = profile
        self.save(profiles)

    def get(self, command: str) -> CommandProfile | None:
        return self.load().get(command)
