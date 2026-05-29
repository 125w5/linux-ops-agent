from __future__ import annotations

import subprocess

from diag.safety.command_checker import check_command


def collect_help(command: str, timeout_seconds: int = 5) -> str:
    shell_command = f"{command} --help"
    decision = check_command(shell_command)
    if not decision.allowed:
        return f"Blocked by safety checker: {decision.reason}"
    try:
        completed = subprocess.run([command, "--help"], text=True, capture_output=True, timeout=timeout_seconds)
    except FileNotFoundError:
        return f"{command}: not found"
    except subprocess.TimeoutExpired:
        return f"{command}: --help timed out"
    return (completed.stdout or completed.stderr or "").strip()
