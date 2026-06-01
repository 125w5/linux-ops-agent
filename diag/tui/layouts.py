from __future__ import annotations

from dataclasses import dataclass

from diag.utils.config_loader import read_config_file
from diag.utils.paths import project_root


@dataclass(frozen=True)
class TuiLayout:
    name: str
    panes: list[str]


def load_layout(name: str = "default") -> TuiLayout:
    path = project_root() / "diag" / "tui" / "layouts" / f"{name}.yaml"
    data = read_config_file(path).get("layout", {})
    panes = data.get("panes", [])
    if not isinstance(panes, list):
        panes = []
    return TuiLayout(str(data.get("name", name)), list(panes))
