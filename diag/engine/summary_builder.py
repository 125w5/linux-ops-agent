from __future__ import annotations

from diag.core.models import DiagnosisOutcome


def build_run_summary(outcome: DiagnosisOutcome | None) -> dict[str, object]:
    if outcome is None:
        return {
            "text": "还没有完成过诊断。先输入 /run 执行一次，我会在结束后用中文总结发生了什么。",
            "risk": "unknown",
            "evidence": [],
            "next_steps": ["先创建或执行诊断计划。"],
        }

    evidence = [f"[{item.severity}] {item.content}" for item in outcome.evidence[:5]]
    causes = outcome.root_causes[:2] or ["这次采集到的证据里还没有明确唯一原因。"]
    suggestions = outcome.suggestions[:3] or ["先复核证据，再决定是否做写入、删除、重启或 kill 操作。"]
    report_line = f"报告：{outcome.markdown_path}" if outcome.markdown_path else "报告：还没有写入完成"
    answer = _answer_for_task(outcome)
    text = "\n".join(
        [
            "诊断完成，我给你总结一下：",
            f"你问的是：{outcome.user_input or outcome.task_type}",
            f"回答：{answer}",
            f"结论：{'; '.join(causes)}",
            "关键证据：",
            *(f"- {item}" for item in evidence[:3] or ["- 这次没有采集到明确证据。"]),
            f"风险：{outcome.risk_level}",
            "下一步建议：",
            *(f"- {item}" for item in suggestions),
            report_line,
        ]
    )
    return {
        "text": text,
        "risk": outcome.risk_level,
        "evidence": evidence,
        "next_steps": suggestions,
        "markdown_path": outcome.markdown_path,
        "json_path": outcome.json_path,
        "actions": [
            {"label": "展开原始输出", "command": "/raw"},
            {"label": "查看报告", "command": "/report"},
            {"label": "解释证据", "command": "解释证据"},
            {"label": "重新检查资源", "command": "/resources"},
        ],
    }


def build_report_summary(outcome: DiagnosisOutcome | None) -> dict[str, object]:
    summary = build_run_summary(outcome)
    if outcome is None:
        return summary
    path = outcome.markdown_path or "报告路径还没有生成"
    text = "\n".join(
        [
            "报告已生成，并且我已经按中文帮你归纳：",
            f"报告位置：{path}",
            str(summary["text"]),
        ]
    )
    return {
        **summary,
        "text": text,
        "message": text,
        "actions": [
            {"label": "展开原始输出", "command": "/raw"},
            {"label": "重新运行诊断", "command": "/run"},
            {"label": "查看资源", "command": "/resources"},
        ],
    }


def _answer_for_task(outcome: DiagnosisOutcome) -> str:
    task = outcome.task_type
    if task == "cpu":
        return "我检查了 CPU 和高占用进程，下面会列出主要证据和风险。"
    if task == "memory":
        return "我检查了内存占用和高内存进程，下面会说明是否异常。"
    if task == "disk":
        return "我检查了磁盘占用、目录/文件证据和可疑增长点。"
    if task == "service":
        return "我检查了服务状态、日志和端口相关证据。"
    if task == "ssh-failure":
        return "我检查了 SSH 登录失败与认证日志证据。"
    return "我已根据当前任务采集证据，并给出可执行的下一步。"
