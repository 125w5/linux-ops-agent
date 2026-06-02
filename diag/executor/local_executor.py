from __future__ import annotations

import platform
import shutil
import subprocess
import time

from diag.core.models import CommandResult


DEMO_OUTPUTS = {
    "df -h": """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        40G   37G  3.0G  93% /
tmpfs           2.0G  120M  1.9G   6% /run
""",
    "du -h --max-depth=1 / 2>/dev/null | sort -hr | head": """18G /var
12G /var/lib/docker
9G /var/log
6G /home
37G /
""",
    "find / -type f -size +500M 2>/dev/null | head": """/var/log/app/big-error.log
/var/lib/docker/overlay2/example/diff/layer.tar
""",
    "journalctl --disk-usage": "Archived and active journals take up 8.7G in the file system.\n",
    "docker system df": """TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          18        6         7.2GB     3.1GB (43%)
Containers      9         2         1.5GB     900MB (60%)
Local Volumes   12        3         3.4GB     2.8GB (82%)
Build Cache     45        0         6.9GB     6.9GB
""",
    "uptime": " 19:40:01 up 21 days,  3:14,  2 users,  load average: 5.82, 4.31, 3.22\n",
    "top -b -n 1 | head -30": """top - 19:40:01 up 21 days,  3:14,  2 users,  load average: 5.82, 4.31, 3.22
Tasks: 188 total,   3 running, 185 sleeping,   0 stopped,   0 zombie
%Cpu(s): 92.1 us,  3.4 sy,  0.0 ni,  4.0 id,  0.2 wa,  0.0 hi,  0.3 si,  0.0 st
MiB Mem :   7960.4 total,    512.1 free,   5421.3 used,   2027.0 buff/cache
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
  21890 app       20   0 1420180 220120  18444 R 187.4   2.7  10:25.61 python
  21902 app       20   0  828340 118004  12428 R  84.1   1.4   4:02.14 java
""",
    "ps aux --sort=-%cpu | head": """USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
app        21890 187.4  2.7 1420180 220120 ?     Rl   19:30  10:25 python worker.py
app        21902  84.1  1.4 828340 118004 ?      Sl   19:34   4:02 java -jar batch.jar
root        1120   3.2  0.4 110000  32000 ?      Ss   May08  44:10 dockerd
""",
    "systemctl status nginx": """x nginx.service - A high performance web server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
     Active: failed (Result: exit-code) since Fri 2026-05-29 19:35:04 CST; 5min ago
    Process: 18332 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=1/FAILURE)
""",
    "journalctl -u nginx -n 50": """May 29 19:35:04 node-01 nginx[18332]: nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
May 29 19:35:04 node-01 nginx[18332]: nginx: configuration file /etc/nginx/nginx.conf test failed
May 29 19:35:04 node-01 systemd[1]: nginx.service: Failed with result 'exit-code'.
May 29 19:35:04 node-01 systemd[1]: Failed to start A high performance web server.
""",
    "ss -tulnp": """Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
tcp   LISTEN 0      511          0.0.0.0:80      0.0.0.0:*     users:(("apache2",pid=1468,fd=4))
tcp   LISTEN 0      128          0.0.0.0:22      0.0.0.0:*     users:(("sshd",pid=912,fd=3))
""",
    "grep 'Failed password' /var/log/auth.log | tail -100": """May 29 19:10:01 node-01 sshd[2101]: Failed password for root from 203.0.113.8 port 51432 ssh2
May 29 19:10:04 node-01 sshd[2103]: Failed password for invalid user admin from 203.0.113.8 port 51444 ssh2
May 29 19:10:08 node-01 sshd[2105]: Failed password for root from 203.0.113.8 port 51451 ssh2
May 29 19:10:15 node-01 sshd[2110]: Failed password for test from 198.51.100.24 port 60001 ssh2
May 29 19:10:22 node-01 sshd[2118]: Failed password for root from 203.0.113.8 port 51488 ssh2
May 29 19:10:24 node-01 sshd[2120]: Failed password for root from 203.0.113.8 port 51491 ssh2
""",
    "grep 'Invalid user' /var/log/auth.log | tail -100": """May 29 19:10:04 node-01 sshd[2103]: Invalid user admin from 203.0.113.8 port 51444
May 29 19:11:31 node-01 sshd[2160]: Invalid user oracle from 198.51.100.24 port 60112
""",
    "grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head": """5 203.0.113.8
1 198.51.100.24
""",
}


class LocalExecutor:
    def __init__(self, timeout_seconds: int = 20, demo: bool = False) -> None:
        self.timeout_seconds = timeout_seconds
        self.demo = demo

    def run(self, command: str, target: str, risk_level: str) -> CommandResult:
        started = time.perf_counter()
        if self.demo:
            stdout = DEMO_OUTPUTS.get(command, "")
            duration_ms = int((time.perf_counter() - started) * 1000)
            return CommandResult(command, target, stdout, "", 0, duration_ms, risk_level)

        if platform.system().lower() != "linux":
            return self._run_windows(command, target, risk_level, started)

        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            executable="/bin/bash",
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return CommandResult(
            command=command,
            target=target,
            stdout=completed.stdout,
            stderr=completed.stderr,
            return_code=completed.returncode,
            duration_ms=duration_ms,
            risk_level=risk_level,
        )

    def _run_windows(self, command: str, target: str, risk_level: str, started: float) -> CommandResult:
        if not shutil.which("wsl.exe"):
            duration_ms = int((time.perf_counter() - started) * 1000)
            return CommandResult(
                command=command,
                target=target,
                stdout="",
                stderr="WSL is not installed. Install Ubuntu with: wsl --install -d Ubuntu",
                return_code=127,
                duration_ms=duration_ms,
                risk_level=risk_level,
            )
        try:
            completed = subprocess.run(
                ["wsl.exe", "bash", "-lc", _prepare_wsl_command(command)],
                capture_output=True,
                timeout=self.timeout_seconds,
            )
            stdout = _decode_process_output(completed.stdout)
            stderr = _decode_process_output(completed.stderr)
            if completed.returncode != 0 and _looks_like_wsl_setup_output(stdout + stderr):
                stdout = ""
                stderr = "WSL is not ready yet. Restart Windows to finish WSL installation. If it still fails after reboot, run: wsl --install -d Ubuntu."
            return_code = completed.returncode
        except (subprocess.TimeoutExpired, OSError) as exc:
            stdout = ""
            stderr = f"WSL command failed: {exc}"
            return_code = 127
        duration_ms = int((time.perf_counter() - started) * 1000)
        return CommandResult(
            command=command,
            target=target,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            duration_ms=duration_ms,
            risk_level=risk_level,
        )


def _decode_process_output(data: bytes | str | None) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    if b"\x00" in data[:200]:
        return data.decode("utf-16-le", errors="replace")
    return data.decode("utf-8", errors="replace")


def _prepare_wsl_command(command: str) -> str:
    rewrites = {
        "du -h --max-depth=1 / 2>/dev/null | sort -hr | head": "du -xh --max-depth=1 / --exclude=/mnt --exclude=/proc --exclude=/sys --exclude=/dev 2>/dev/null | sort -hr | head",
        "find / -type f -size +500M 2>/dev/null | head": "find / \\( -path /mnt -o -path /proc -o -path /sys -o -path /dev \\) -prune -o -type f -size +500M -print 2>/dev/null | head",
    }
    return rewrites.get(command, command)


def _looks_like_wsl_setup_output(text: str) -> bool:
    lowered = text.lower()
    return "wsl_e_wsl_optional_component_required" in lowered or (
        "wsl.exe" in lowered and "--install" in lowered and ("ubuntu" in lowered or "distribution" in lowered)
    )
