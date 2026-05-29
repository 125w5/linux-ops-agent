from __future__ import annotations

from diag.tooldocs.command_profile import CommandProfile, extract_flags


SCENE_COMMANDS = {
    "disk": ("df", "du", "find", "journalctl", "docker"),
    "cpu": ("uptime", "top", "ps"),
    "service-failed": ("systemctl", "journalctl", "ss"),
    "ssh-failure": ("grep", "awk", "tail", "sort", "uniq"),
}


def build_profile(command: str, help_text: str, man_text: str) -> CommandProfile:
    combined = "\n".join([help_text, man_text])
    mutating_words = ("remove", "delete", "write", "modify", "kill", "restart", "stop", "start", "prune")
    return CommandProfile(
        command=command,
        help_text=help_text,
        man_text=man_text,
        flags=extract_flags(combined),
        likely_readonly=not any(word in combined.lower() for word in mutating_words),
    )


def suggest_for_scene(scene: str, profiles: dict[str, CommandProfile]) -> list[str]:
    commands = SCENE_COMMANDS.get(scene, ())
    suggestions: list[str] = []
    for command in commands:
        profile = profiles.get(command)
        if not profile:
            suggestions.append(f"Index local docs for {command} before considering it for scene {scene}.")
            continue
        readonly = "read-only-looking" if profile.likely_readonly else "needs extra review"
        suggestions.append(f"{command}: {readonly}; discovered {len(profile.flags)} flags. Review before adding to runbook.")
    return suggestions
