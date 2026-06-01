from __future__ import annotations

from diag.plugins.manifest import PluginManifest
from diag.plugins.validator import FORBIDDEN_PERMISSIONS


def sandbox_allows(manifest: PluginManifest) -> tuple[bool, str]:
    forbidden = FORBIDDEN_PERMISSIONS.intersection(set(manifest.permissions))
    if forbidden:
        return False, f"Forbidden plugin permissions: {', '.join(sorted(forbidden))}"
    return True, "plugin sandbox policy passed"
