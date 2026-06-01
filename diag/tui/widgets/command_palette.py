from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaletteCommand:
    name: str
    description: str
    shortcut: str = ""
    source: str = "core"


@dataclass
class CommandPaletteState:
    commands: list[PaletteCommand]
    query: str = ""
    selected_index: int = 0
    open: bool = False

    @property
    def filtered(self) -> list[PaletteCommand]:
        return filter_commands(self.query, self.commands)

    @property
    def selected(self) -> PaletteCommand | None:
        items = self.filtered
        if not items:
            return None
        return items[self.selected_index % len(items)]

    def input(self, text: str) -> None:
        self.query += text
        self.selected_index = 0

    def backspace(self) -> None:
        self.query = self.query[:-1]
        self.selected_index = 0

    def move(self, delta: int) -> None:
        if self.filtered:
            self.selected_index = (self.selected_index + delta) % len(self.filtered)

    def execute_selected(self) -> str | None:
        selected = self.selected
        return selected.name if selected else None


CORE_COMMANDS = [
    PaletteCommand("/plan", "Show or create diagnosis plan", "p"),
    PaletteCommand("/run", "Run current plan", "F5/Ctrl+R"),
    PaletteCommand("/approve", "Approve pending low-risk command", "Ctrl+A"),
    PaletteCommand("/deny", "Deny pending command", "Ctrl+D"),
    PaletteCommand("/evidence", "Show evidence chain", "F6"),
    PaletteCommand("/raw", "Toggle raw output", "F2"),
    PaletteCommand("/report", "Show report preview/path", "F4"),
    PaletteCommand("/resources", "Show resource usage", "F3"),
    PaletteCommand("/model", "Inspect or switch model", "F8"),
    PaletteCommand("/plugin", "Inspect plugins", "F7"),
    PaletteCommand("/skill", "Inspect or select skill"),
    PaletteCommand("/layout", "Switch layout", "Ctrl+L"),
    PaletteCommand("/style", "Switch output style"),
    PaletteCommand("/config", "Open config screen"),
    PaletteCommand("/help", "Open help", "F1"),
    PaletteCommand("/exit", "Exit TUI"),
]


def palette_commands(extra: list[PaletteCommand] | None = None) -> list[PaletteCommand]:
    return CORE_COMMANDS + list(extra or [])


def plugin_command(name: str, description: str, shortcut: str = "") -> PaletteCommand:
    return PaletteCommand(name=name, description=description, shortcut=shortcut, source="plugin")


def skill_command(name: str, description: str, shortcut: str = "") -> PaletteCommand:
    return PaletteCommand(name=name, description=description, shortcut=shortcut, source="skill")


def filter_commands(query: str, commands: list[PaletteCommand] | None = None) -> list[PaletteCommand]:
    source = commands or CORE_COMMANDS
    needle = query.lower().strip()
    if not needle:
        return list(source)
    return [command for command in source if needle in command.name.lower() or needle in command.description.lower()]


def render_palette(state: CommandPaletteState) -> str:
    lines = [f"Command Palette /{state.query}"]
    for index, command in enumerate(state.filtered):
        marker = ">" if index == state.selected_index else " "
        lines.append(f"{marker} {command.name:<12} {command.shortcut:<10} {command.description} [{command.source}]")
    return "\n".join(lines)
