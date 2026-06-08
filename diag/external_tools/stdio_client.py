from __future__ import annotations

from diag.external_tools.manifest import ExternalToolManifest


class ExternalToolClient:
    def __init__(self, manifest: ExternalToolManifest) -> None:
        manifest.validate()
        self.manifest = manifest

    def call(self, _payload: dict) -> dict:
        return {"ok": False, "error": "external tools are disabled by default"}
