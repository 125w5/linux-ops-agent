from __future__ import annotations


SLASH_COMMANDS = [
    "/plan",
    "/run",
    "/approve",
    "/deny",
    "/evidence",
    "/raw",
    "/report",
    "/status",
    "/resources",
    "/model",
    "/style",
    "/plugin",
    "/skill",
    "/mode",
    "/history",
    "/help",
    "/exit",
]


def render_help() -> str:
    return "Interactive commands:\n" + "\n".join(f"- {command}" for command in SLASH_COMMANDS)
