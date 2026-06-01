from __future__ import annotations

from diag.ai.config import resolve_provider_config
from diag.ai.model_router import build_provider
from diag.plugins.loader import PluginLoader
from diag.utils.paths import project_root, report_dir, transcript_dir


def health_report() -> tuple[bool, str]:
    lines: list[str] = []
    ok = True
    for path in [project_root(), report_dir(), transcript_dir()]:
        writable = path.exists() or path.parent.exists()
        lines.append(f"[{'ok' if writable else 'fail'}] path {path}")
        ok = ok and writable
    provider = build_provider(resolve_provider_config(provider="mock"))
    health = provider.healthcheck()
    lines.append(f"[{'ok' if health.ok else 'fail'}] provider {health.provider}: {health.message}")
    plugins = PluginLoader().discover().list()
    invalid = [record.manifest.name for record in plugins if not record.valid]
    lines.append(f"[{'ok' if not invalid else 'fail'}] plugins: {len(plugins)} discovered")
    if invalid:
        ok = False
        lines.append(f"invalid plugins: {', '.join(invalid)}")
    return ok, "\n".join(lines)
