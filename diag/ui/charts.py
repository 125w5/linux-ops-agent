from __future__ import annotations


def bar(label: str, value: float, max_value: float = 100.0, width: int = 24) -> str:
    if max_value <= 0:
        max_value = 1
    ratio = max(0.0, min(1.0, value / max_value))
    filled = int(ratio * width)
    return f"{label:<12} [{'#' * filled}{'.' * (width - filled)}] {value:g}"


def risk_bar(risk: str, width: int = 24) -> str:
    values = {"info": 25, "warning": 60, "critical": 95}
    return bar("risk", values.get(risk, 25), 100, width)


def disk_bar(label: str, used_percent: float, width: int = 24) -> str:
    return bar(label, used_percent, 100, width)


def cpu_bar(label: str, used_percent: float, width: int = 24) -> str:
    return bar(label, used_percent, 100, width)
