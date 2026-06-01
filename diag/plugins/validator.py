from __future__ import annotations

from diag.core.models import RiskLevel
from diag.plugins.errors import PluginValidationError
from diag.plugins.manifest import PluginManifest
from diag.safety.command_checker import check_command
from diag.tools.spec import ToolSpec


FORBIDDEN_PERMISSIONS = {"execute", "shell", "write", "network", "danger-full-access"}
ALLOWED_EXPORTS = {"tools", "runbooks", "analyzers", "hooks"}


def validate_manifest(manifest: PluginManifest) -> list[str]:
    errors: list[str] = []
    if not manifest.name:
        errors.append("missing name")
    if not manifest.version:
        errors.append("missing version")
    if not manifest.entry:
        errors.append("missing entry")
    forbidden = FORBIDDEN_PERMISSIONS.intersection(set(manifest.permissions))
    if forbidden:
        errors.append(f"forbidden permissions: {', '.join(sorted(forbidden))}")
    invalid_exports = set(manifest.exports).difference(ALLOWED_EXPORTS)
    if invalid_exports:
        errors.append(f"invalid exports: {', '.join(sorted(invalid_exports))}")
    return errors


def validate_tool_spec(spec: ToolSpec) -> None:
    if spec.risk in {RiskLevel.HIGH_RISK, RiskLevel.BLOCKED}:
        raise PluginValidationError(f"Plugin tool {spec.name} declares unsafe risk {spec.risk.value}")
    decision = check_command(spec.render({"service": "nginx"}))
    if not decision.allowed:
        raise PluginValidationError(f"Plugin tool {spec.name} is blocked by safety checker: {decision.reason}")
