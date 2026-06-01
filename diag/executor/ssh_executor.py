from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass

from diag.core.models import CommandResult
from diag.utils.config_loader import load_config


@dataclass(frozen=True)
class SSHHostConfig:
    name: str
    host: str
    user: str | None = None
    port: int = 22
    identity_file: str | None = None
    connect_timeout: int = 10


def load_ssh_host(target: str) -> SSHHostConfig | None:
    hosts = load_config().get("hosts", {})
    data = hosts.get(target, {}) if isinstance(hosts, dict) else {}
    if not data:
        return None
    return SSHHostConfig(
        name=target,
        host=str(data.get("host", target)),
        user=str(data.get("user")) if data.get("user") else None,
        port=int(data.get("port", 22)),
        identity_file=str(data.get("identity_file")) if data.get("identity_file") else None,
        connect_timeout=int(data.get("connect_timeout", 10)),
    )


class SSHExecutor:
    def __init__(self, timeout_seconds: int = 20, demo: bool = False) -> None:
        self.timeout_seconds = timeout_seconds
        self.demo = demo

    def run(self, command: str, target: str, risk_level: str) -> CommandResult:
        started = time.perf_counter()
        if self.demo:
            return CommandResult(
                command,
                target,
                "",
                "SSH execution is disabled in demo mode.",
                126,
                int((time.perf_counter() - started) * 1000),
                risk_level,
                skipped=True,
            )

        host_config = load_ssh_host(target)
        if not host_config:
            return CommandResult(
                command,
                target,
                "",
                f"SSH target not found in configs/hosts.yaml: {target}",
                127,
                int((time.perf_counter() - started) * 1000),
                risk_level,
                skipped=True,
            )

        destination = host_config.host if not host_config.user else f"{host_config.user}@{host_config.host}"
        args = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={host_config.connect_timeout}",
            "-p",
            str(host_config.port),
        ]
        if host_config.identity_file:
            args.extend(["-i", host_config.identity_file])
        args.extend([destination, shlex.quote(command)])
        try:
            completed = subprocess.run(args, text=True, capture_output=True, timeout=self.timeout_seconds)
            return_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except FileNotFoundError:
            return_code = 127
            stdout = ""
            stderr = "OpenSSH client not found. Install ssh or run without --ssh."
        except subprocess.TimeoutExpired:
            return_code = 124
            stdout = ""
            stderr = f"SSH command timed out after {self.timeout_seconds}s."
        duration_ms = int((time.perf_counter() - started) * 1000)
        return CommandResult(command, target, stdout, stderr, return_code, duration_ms, risk_level)
