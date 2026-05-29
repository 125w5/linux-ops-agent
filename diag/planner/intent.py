from __future__ import annotations


TASK_ALIASES = {
    "disk": ("disk", "space", "full", "du", "df", "磁盘", "空间", "满", "容量"),
    "cpu": ("cpu", "load", "slow", "卡", "负载", "高占用"),
    "service": ("service", "systemctl", "nginx", "failed", "启动", "服务"),
    "ssh-failure": ("ssh", "ssh-failure", "login", "auth", "password", "登录", "暴力", "失败"),
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
