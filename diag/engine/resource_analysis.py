from __future__ import annotations

from typing import Any


def analyze_resource_snapshot(snapshot: dict[str, Any], *, focus: str = "overview") -> dict[str, Any]:
    status = str(snapshot.get("sampler_status") or "unknown")
    sampler_error = snapshot.get("sampler_error")
    cpu = _number(snapshot.get("system_cpu_percent"))
    memory = _dict(snapshot.get("memory"))
    disk = _dict(snapshot.get("disk"))
    memory_percent = _number(memory.get("percent"))
    disk_percent = _number(disk.get("percent"))
    top_cpu = _rows(snapshot.get("top_cpu") or snapshot.get("top_cpu_processes"))
    top_memory = _rows(snapshot.get("top_memory") or snapshot.get("top_memory_processes"))

    risk = _risk(cpu, memory_percent, disk_percent, status)
    conclusion = _conclusion(focus, risk, status, cpu, memory_percent, disk_percent, top_cpu, top_memory)
    evidence = _evidence(status, sampler_error, cpu, memory, disk, top_cpu, top_memory, snapshot)
    next_steps = _next_steps(focus, risk, status, top_cpu, top_memory)

    text = _render_analysis(conclusion, evidence, risk, next_steps)
    return {
        "text": text,
        "conclusion": conclusion,
        "evidence": evidence,
        "risk": risk,
        "next_steps": next_steps,
        "actions": _actions(focus, top_cpu, top_memory),
    }


def analyze_process_rows(items: list[dict[str, Any]], *, focus: str = "cpu", snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = snapshot or {}
    status = str(snapshot.get("sampler_status") or "unknown")
    rows = _rows(items)
    if not rows:
        conclusion = "还没有拿到进程采样。"
        evidence = [f"sampler_status={status}", "Top process list is empty."]
        risk = "info" if status in {"warming_up", "starting"} else "warning"
        next_steps = ["等待下一次 telemetry heartbeat，或运行 /monitor doctor 查看采样原因。"]
    else:
        top = rows[0]
        name = str(top.get("name") or "?")
        pid = top.get("pid", "?")
        normalized = _number(top.get("normalized_cpu_percent"), top.get("cpu_percent")) or 0.0
        raw = _number(top.get("raw_cpu_percent")) or normalized
        memory_mb = _memory_mb(top)
        if focus == "memory":
            conclusion = f"当前内存最高的是 {name} (PID {pid})，约 {memory_mb:.0f}MB。"
            risk = "warning" if memory_mb >= 1024 else "info"
        else:
            conclusion = f"当前 CPU 最高的是 {name} (PID {pid})，约 {normalized:.1f}% system / {raw:.0f}% raw。"
            risk = "critical" if normalized >= 85 else "warning" if normalized >= 60 else "info"
        evidence = [_format_process_evidence(row) for row in rows[:3]]
        next_steps = [
            f"先 Inspect PID {pid} 看命令行与所属用户。",
            "如果确认异常，优先 SIGTERM；SIGKILL 默认阻止或需要更严格审批。",
            "3 秒后 Refresh 复查进程是否仍在高占用。",
        ]

    text = _render_analysis(conclusion, evidence, risk, next_steps)
    return {
        "text": text,
        "conclusion": conclusion,
        "evidence": evidence,
        "risk": risk,
        "next_steps": next_steps,
        "actions": _actions("memory" if focus == "memory" else "cpu", rows, rows),
    }


def _render_analysis(conclusion: str, evidence: list[str], risk: str, next_steps: list[str]) -> str:
    lines = [
        f"结论：{conclusion}",
        f"风险：{risk}",
        "关键证据：",
    ]
    lines.extend(f"- {item}" for item in evidence[:5])
    lines.append("下一步：")
    lines.extend(f"- {item}" for item in next_steps[:4])
    return "\n".join(lines)


def _conclusion(
    focus: str,
    risk: str,
    status: str,
    cpu: float | None,
    memory_percent: float | None,
    disk_percent: float | None,
    top_cpu: list[dict[str, Any]],
    top_memory: list[dict[str, Any]],
) -> str:
    if status in {"starting", "warming_up"}:
        return "telemetry 正在预热，当前结论只作为初步观察。"
    if status in {"error", "stalled"}:
        return "telemetry 没有完整采样，先看错误原因，不要根据 n/a 做判断。"
    if focus == "cpu" and top_cpu:
        row = top_cpu[0]
        return f"CPU 主要由 {row.get('name', '?')} (PID {row.get('pid', '?')}) 占用。"
    if focus == "memory" and top_memory:
        row = top_memory[0]
        return f"内存主要由 {row.get('name', '?')} (PID {row.get('pid', '?')}) 占用。"
    if risk in {"critical", "warning"}:
        hot = []
        if cpu is not None and cpu >= 70:
            hot.append(f"CPU {cpu:.0f}%")
        if memory_percent is not None and memory_percent >= 75:
            hot.append(f"MEM {memory_percent:.0f}%")
        if disk_percent is not None and disk_percent >= 80:
            hot.append(f"DISK {disk_percent:.0f}%")
        return "资源存在压力：" + ", ".join(hot)
    return "当前资源指标没有明显高压信号。"


def _evidence(
    status: str,
    sampler_error: Any,
    cpu: float | None,
    memory: dict[str, Any],
    disk: dict[str, Any],
    top_cpu: list[dict[str, Any]],
    top_memory: list[dict[str, Any]],
    snapshot: dict[str, Any],
) -> list[str]:
    evidence = [f"sampler_status={status}"]
    if sampler_error:
        evidence.append(f"sampler_error={sampler_error}")
    if cpu is not None:
        evidence.append(f"system_cpu={cpu:.1f}%")
    mem_percent = _number(memory.get("percent"))
    if mem_percent is not None:
        evidence.append(f"memory={_bytes(memory.get('used_bytes'))} / {_bytes(memory.get('total_bytes'))} ({mem_percent:.1f}%)")
    disk_percent = _number(disk.get("percent"))
    if disk_percent is not None:
        mount = str(disk.get("mount") or "disk")
        evidence.append(f"disk {mount}={_bytes(disk.get('used_bytes'))} / {_bytes(disk.get('total_bytes'))} ({disk_percent:.1f}%)")
    if top_cpu:
        evidence.append("top_cpu: " + "; ".join(_format_process_brief(row, cpu=True) for row in top_cpu[:3]))
    if top_memory:
        evidence.append("top_mem: " + "; ".join(_format_process_brief(row, cpu=False) for row in top_memory[:3]))
    denied = _number(snapshot.get("permission_denied_count"))
    if denied:
        evidence.append(f"permission_denied_count={int(denied)}")
    return evidence


def _next_steps(focus: str, risk: str, status: str, top_cpu: list[dict[str, Any]], top_memory: list[dict[str, Any]]) -> list[str]:
    if status in {"starting", "warming_up"}:
        return ["等待 1-2 秒再次 Refresh。", "如果一直没有样本，运行 /monitor doctor。"]
    if status in {"error", "stalled"}:
        return ["运行 /monitor doctor 查看 Python/psutil/engine stderr。", "确认 opspilot.cmd 使用的 Python 与你安装 psutil 的 Python 一致。"]
    steps = []
    if focus == "cpu" and top_cpu:
        steps.append(f"Inspect PID {top_cpu[0].get('pid', '?')}，确认命令行和所属用户。")
    elif focus == "memory" and top_memory:
        steps.append(f"Inspect PID {top_memory[0].get('pid', '?')}，确认是否预期占用。")
    else:
        steps.append("继续观察资源趋势，必要时切到 Process 面板。")
    if risk in {"critical", "warning"}:
        steps.append("先收集证据再处理；不要直接 kill 系统或 OpsPilot 自身进程。")
    steps.append("Refresh 后比较 raw 与 normalized CPU，避免把多核 raw 百分比误判为整机 CPU。")
    return steps


def _risk(cpu: float | None, memory_percent: float | None, disk_percent: float | None, status: str) -> str:
    if status in {"error", "stalled"}:
        return "warning"
    if any(value is not None and value >= limit for value, limit in ((cpu, 90), (memory_percent, 90), (disk_percent, 90))):
        return "critical"
    if any(value is not None and value >= limit for value, limit in ((cpu, 70), (memory_percent, 75), (disk_percent, 80))):
        return "warning"
    return "info"


def _actions(focus: str, top_cpu: list[dict[str, Any]], top_memory: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = top_memory if focus == "memory" else top_cpu
    actions: list[dict[str, str]] = []
    for row in rows[:1]:
        pid = row.get("pid")
        if pid is None:
            continue
        actions.extend(
            [
                {"label": f"Inspect {pid}", "command": f"/process inspect {pid}"},
                {"label": f"Show tree {pid}", "command": f"/process tree {pid}"},
                {"label": f"SIGTERM {pid}", "command": f"/process term {pid}"},
            ]
        )
    actions.extend(
        [
            {"label": "Refresh", "command": "/process" if focus in {"cpu", "memory"} else "/resources"},
            {"label": "Telemetry doctor", "command": "/monitor doctor"},
        ]
    )
    return actions


def _format_process_evidence(row: dict[str, Any]) -> str:
    return (
        f"PID {row.get('pid', '?')} {row.get('name', '?')} "
        f"CPU {_number(row.get('normalized_cpu_percent'), row.get('cpu_percent')) or 0:.1f}% system / "
        f"{_number(row.get('raw_cpu_percent')) or 0:.0f}% raw, MEM {_memory_mb(row):.0f}MB"
    )


def _format_process_brief(row: dict[str, Any], *, cpu: bool) -> str:
    if cpu:
        return f"{row.get('name', '?')}({row.get('pid', '?')}) {_number(row.get('normalized_cpu_percent'), row.get('cpu_percent')) or 0:.1f}%/{_number(row.get('raw_cpu_percent')) or 0:.0f}% raw"
    return f"{row.get('name', '?')}({row.get('pid', '?')}) {_memory_mb(row):.0f}MB"


def _memory_mb(row: dict[str, Any]) -> float:
    value = _number(row.get("memory_mb"))
    if value is not None:
        return value
    bytes_value = _number(row.get("memory_bytes"))
    return 0.0 if bytes_value is None else bytes_value / 1024 / 1024


def _bytes(value: Any) -> str:
    number = _number(value)
    if number is None or number <= 0:
        return "n/a"
    gb = number / 1024 / 1024 / 1024
    if gb >= 1:
        return f"{gb:.0f}G"
    return f"{number / 1024 / 1024:.0f}M"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
    return None
