from __future__ import annotations

from typing import Any

from diag.dashboard.disk_view import disk_line
from diag.dashboard.process_view import compact_processes
from diag.dashboard.view_model import DashboardViewModel, ToolCallView


def render_plain_dashboard(vm: DashboardViewModel, *, raw_expanded: bool = False) -> str:
    lines = [
        _header(vm),
        _resource_line(vm.resources),
        "",
        "Plan / Tool Calls",
    ]
    if vm.tool_calls:
        lines.extend(_tool_line(call) for call in vm.tool_calls)
    else:
        lines.append("- waiting for plan")

    lines.extend(["", "Evidence"])
    if vm.evidence:
        lines.extend(f"- [{item.get('severity', 'info')}] {item.get('content', '')}" for item in vm.evidence[-6:])
    else:
        lines.append("- waiting for evidence")

    lines.extend(["", "Resources"])
    lines.extend(_resource_details(vm.resources))

    lines.extend(["", "Raw Summary"])
    if raw_expanded:
        lines.extend(f"- {item}" for item in (vm.raw_summary or ["no raw command summary yet"]))
    else:
        lines.append(f"- folded ({len(vm.raw_summary)} command summaries); use --view raw to expand")

    lines.extend(["", "Report Preview"])
    if vm.report_preview:
        lines.extend(f"- {item}" for item in vm.report_preview[:6])
    elif vm.report_path:
        lines.append(f"- report ready: {vm.report_path}")
    else:
        lines.append("- report pending")

    if vm.report_path:
        lines.append(f"Markdown report: {vm.report_path}")
    if vm.json_path:
        lines.append(f"JSON report: {vm.json_path}")

    lines.extend(["", command_discovery_text()])
    return "\n".join(lines)


def render_rich_dashboard(vm: DashboardViewModel, *, raw_expanded: bool = False) -> Any:
    try:
        from rich.console import Group
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.table import Table
    except Exception:
        return render_plain_dashboard(vm, raw_expanded=raw_expanded)

    layout = Layout(name="root")
    layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=8))
    layout["body"].split_row(Layout(name="left", ratio=2), Layout(name="right", ratio=1))
    layout["left"].split_column(Layout(name="plan", ratio=2), Layout(name="evidence", ratio=1), Layout(name="raw", ratio=1))
    layout["right"].split_column(Layout(name="resources", ratio=1), Layout(name="report", ratio=1))

    layout["header"].update(Panel(_header(vm), title="StatusLine", border_style="cyan"))
    layout["plan"].update(Panel(_tool_table(vm.tool_calls), title="Plan / Tool Calls", border_style="green"))
    layout["evidence"].update(Panel("\n".join(_evidence_lines(vm)), title="Evidence", border_style="yellow"))
    layout["raw"].update(Panel("\n".join(_raw_lines(vm, raw_expanded)), title="Raw Summary", border_style="blue"))
    layout["resources"].update(Panel("\n".join([_resource_line(vm.resources), *_resource_details(vm.resources)]), title="System Monitor", border_style="magenta"))
    layout["report"].update(Panel("\n".join(_report_lines(vm)), title="Report Preview", border_style="white"))
    layout["footer"].update(Panel(command_discovery_text(), title="Commands", border_style="cyan"))
    return Group(layout)


def command_discovery_text() -> str:
    return "\n".join(
        [
            "Commands:",
            "  diag tui      打开全屏工作台",
            "  diag chat     进入交互诊断",
            "  --view raw    展开原始输出",
            "  --view plain  纯文本输出",
            "  /help         chat/tui 中查看命令",
        ]
    )


def _header(vm: DashboardViewModel) -> str:
    session = vm.session_id[:8] if vm.session_id else "pending"
    return (
        f"OpsPilot-Linux | session={session} | task={vm.task or 'pending'} | "
        f"target={vm.target} | mode={vm.mode} | risk={vm.risk} | status={vm.status}"
    )


def _resource_line(resources: dict[str, Any]) -> str:
    system = resources.get("system") or {}
    cpu = system.get("cpu_percent")
    mem_used = system.get("memory_used_gb")
    mem_total = system.get("memory_total_gb")
    mem_percent = system.get("memory_percent")
    cpu_text = "CPU n/a" if cpu is None else f"CPU {float(cpu):.1f}%"
    mem_text = "Mem n/a"
    if mem_used is not None and mem_total is not None and mem_percent is not None:
        mem_text = f"Mem {float(mem_used):.1f}/{float(mem_total):.1f}GB {float(mem_percent):.1f}%"
    return f"{cpu_text} | {mem_text} | {disk_line(resources)}"


def _resource_details(resources: dict[str, Any]) -> list[str]:
    system = resources.get("system") or {}
    load = system.get("load_average") or []
    load_text = ", ".join(f"{float(item):.2f}" for item in load[:3]) if load else "n/a"
    return [
        f"- load average: {load_text}",
        f"- top cpu: {compact_processes(resources.get('top_cpu_processes') or [], 'cpu_percent')}",
        f"- top memory: {compact_processes(resources.get('top_memory_processes') or [], 'memory_percent')}",
        f"- commands: started={resources.get('commands_started', 0)} executed={resources.get('commands_executed', 0)} skipped={resources.get('commands_skipped', 0)}",
        f"- ai calls: {resources.get('ai_calls', 0)}",
    ]


def _tool_line(call: ToolCallView) -> str:
    name = call.tool_name or call.name or call.step_id
    risk = f" risk={call.risk}" if call.risk else ""
    return f"- [{call.status}] {name}: `{call.command}`{risk}"


def _tool_table(tool_calls: list[ToolCallView]) -> Any:
    from rich.table import Table

    table = Table(expand=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Tool")
    table.add_column("Command")
    table.add_column("Risk", no_wrap=True)
    rows = tool_calls or [ToolCallView(step_id="", tool_name="waiting", command="waiting for plan")]
    for call in rows:
        table.add_row(call.status, call.tool_name or call.step_id, call.command, call.risk)
    return table


def _evidence_lines(vm: DashboardViewModel) -> list[str]:
    if not vm.evidence:
        return ["waiting for evidence"]
    return [f"[{item.get('severity', 'info')}] {item.get('content', '')}" for item in vm.evidence[-8:]]


def _raw_lines(vm: DashboardViewModel, raw_expanded: bool) -> list[str]:
    if raw_expanded:
        return vm.raw_summary or ["no raw command summary yet"]
    return [f"folded ({len(vm.raw_summary)} command summaries)", "use --view raw to expand"]


def _report_lines(vm: DashboardViewModel) -> list[str]:
    if vm.report_preview:
        lines = vm.report_preview[:8]
    elif vm.report_path:
        lines = [f"report ready: {vm.report_path}"]
    else:
        lines = ["report pending"]
    if vm.report_path:
        lines.append(f"Markdown: {vm.report_path}")
    if vm.json_path:
        lines.append(f"JSON: {vm.json_path}")
    return lines
