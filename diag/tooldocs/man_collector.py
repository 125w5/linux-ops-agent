from __future__ import annotations

import os
import subprocess

from diag.safety.command_checker import check_command


def collect_man(command: str, timeout_seconds: int = 5) -> str:
    shell_command = f"man {command}"
    decision = check_command(shell_command)
    if not decision.allowed:
        return f"Blocked by safety checker: {decision.reason}"
    env = dict(os.environ)
    env["MANPAGER"] = "cat"
    try:
        completed = subprocess.run(["man", command], text=True, capture_output=True, timeout=timeout_seconds, env=env)
    except FileNotFoundError:
        return "man: not found"
    except subprocess.TimeoutExpired:
        return f"man {command}: timed out"
    return (completed.stdout or completed.stderr or "").strip()
