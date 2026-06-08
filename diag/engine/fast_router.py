from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from typing import Any, Callable


FAST_COMMANDS = {
    "/help",
    "/config",
    "/model",
    "/plugin",
    "/resources",
    "/raw",
    "/report",
    "/exit",
    "/permissions",
    "/approve",
    "/deny",
    "/cancel",
    "/fast",
    "/compact",
    "/agents",
    "/tools",
    "/doctor",
    "/monitor",
    "/telemetry",
    "/latency",
    "/process",
    "/cost",
    "/usage",
    "/session",
    "/resume",
    "/clear",
    "/rewind",
}

FAST_WORDS = {
    "你好",
    "您好",
    "hi",
    "hello",
    "hey",
    "配置 api",
    "配置api",
    "换模型",
    "执行",
    "批准",
    "拒绝",
    "查看报告",
    "展开 raw",
}

PROCESS_WORDS = {
    "哪个进程占 cpu",
    "找出高 cpu 进程",
    "高 cpu 进程",
    "哪些进程占内存",
    "查看内存占用",
    "内存占用",
    "内存使用",
    "占内存",
    "占 cpu",
    "能不能杀掉这个进程",
    "kill 进程",
    "杀掉进程",
    "查看进程树",
    "process",
    "top cpu",
    "top memory",
}

KNOWN_OPS_WORDS = {
    "disk",
    "cpu",
    "memory",
    "process",
    "nginx",
    "docker",
    "systemd",
    "port",
    "ssh",
    "journal",
    "mysql",
    "service",
    "磁盘",
    "内存",
    "进程",
    "端口",
    "日志",
    "服务",
    "故障",
    "异常",
    "失败",
    "报错",
}


@dataclass(frozen=True)
class FastRoute:
    fast: bool
    reason: str


@dataclass(frozen=True)
class TimeoutFallback:
    result: Any | None
    fallback: bool
    reason: str
    latency_ms: int


def route_fast_path(text: str) -> FastRoute:
    normalized = text.strip().lower()
    if not normalized:
        return FastRoute(True, "empty")
    if any(normalized == command or normalized.startswith(command + " ") for command in FAST_COMMANDS):
        return FastRoute(True, "slash_command")
    if any(word in normalized for word in FAST_WORDS):
        return FastRoute(True, "common_intent")
    if is_process_query(normalized):
        return FastRoute(True, "process_query")
    if is_known_ops_task(normalized):
        return FastRoute(True, "known_ops_task")
    return FastRoute(False, "complex_or_fault")


def should_call_api_for_input(text: str) -> bool:
    return not route_fast_path(text).fast and should_use_remote_planner(text)


def call_with_timeout_fallback(
    fn: Callable[[], Any],
    *,
    timeout_seconds: float = 8.0,
    fallback_result: Any | None = None,
) -> TimeoutFallback:
    import time

    started = time.perf_counter()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        result = future.result(timeout=timeout_seconds)
        return TimeoutFallback(result, False, "", int((time.perf_counter() - started) * 1000))
    except concurrent.futures.TimeoutError:
        future.cancel()
        return TimeoutFallback(fallback_result, True, "api_timeout", int((time.perf_counter() - started) * 1000))
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def should_use_remote_planner(_text: str) -> bool:
    return False


def is_process_query(text: str) -> bool:
    normalized = text.strip().lower()
    return any(word in normalized for word in PROCESS_WORDS)


def is_known_ops_task(text: str) -> bool:
    normalized = text.strip().lower()
    return any(word in normalized for word in KNOWN_OPS_WORDS)
