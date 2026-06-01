from __future__ import annotations

from pathlib import Path

from diag.utils.paths import project_root


class InputHistory:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or project_root() / "outputs" / "history" / "chat_history.txt"

    def append(self, text: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(text.replace("\n", " ") + "\n")

    def tail(self, limit: int = 20) -> list[str]:
        if not self.path.exists():
            return []
        return self.path.read_text(encoding="utf-8").splitlines()[-limit:]
