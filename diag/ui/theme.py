from __future__ import annotations

from dataclasses import dataclass

from diag.utils.config_loader import load_config


@dataclass(frozen=True)
class OutputStyle:
    name: str
    title: str
    risk_label: str
    suggestions_label: str


def load_output_style(name: str | None = None) -> OutputStyle:
    config = load_config()
    styles = config.get("output_styles", {})
    selected = name or styles.get("default", "ops")
    data = styles.get(selected, styles.get("ops", {}))
    return OutputStyle(
        name=selected,
        title=str(data.get("title", "Ops Diagnosis")),
        risk_label=str(data.get("risk_label", "Risk")),
        suggestions_label=str(data.get("suggestions_label", "Suggestions")),
    )


def terminal_width(default: int = 100) -> int:
    try:
        import shutil

        return shutil.get_terminal_size((default, 24)).columns
    except OSError:
        return default
