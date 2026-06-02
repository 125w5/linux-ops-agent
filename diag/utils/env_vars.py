from __future__ import annotations

import os


def get_env_var(name: str | None) -> str | None:
    if not name:
        return None
    value = os.environ.get(name)
    if value:
        return value
    if os.name != "nt":
        return None
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _kind = winreg.QueryValueEx(key, name)
    except OSError:
        return None
    return str(value) if value else None
