from __future__ import annotations


TASK_ALIASES = {
    "ssh-failure": (
        "ssh",
        "ssh-failure",
        "sshd",
        "auth",
        "auth.log",
        "login",
        "failed password",
        "invalid user",
        "password",
        "登录失败",
        "登陆失败",
        "认证失败",
        "密码失败",
        "ssh失败",
        "暴力",
        "爆破",
    ),
    "disk": ("disk", "space", "full", "du", "df", "filesystem", "磁盘", "空间", "满", "容量", "硬盘"),
    "cpu": ("cpu", "load", "slow", "processor", "卡", "负载", "高占用", "处理器"),
    "service": ("service", "systemctl", "nginx", "failed", "启动", "服务", "端口", "systemd"),
}


def infer_task(user_input: str | None, explicit_task: str | None) -> str:
    if explicit_task:
        normalized = explicit_task.strip().lower()
        if normalized == "ssh":
            normalized = "ssh-failure"
        if normalized in TASK_ALIASES:
            return normalized
        raise ValueError(f"Unsupported task: {explicit_task}")

    text = (user_input or "").lower()
    for task, aliases in TASK_ALIASES.items():
        if any(alias in text for alias in aliases):
            return task
    return "disk"
