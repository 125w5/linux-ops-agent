from __future__ import annotations


class PluginError(RuntimeError):
    pass


class PluginValidationError(PluginError):
    pass
