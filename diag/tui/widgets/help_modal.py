from __future__ import annotations

from diag.tui.widgets.command_palette import palette_commands


def render_help_modal() -> str:
    return "\n".join(f"{command.name:<12} {command.shortcut:<10} {command.description} [{command.source}]" for command in palette_commands())
