from __future__ import annotations

from enum import Enum


class TuiAction(str, Enum):
    HELP = "help"
    RAW = "raw"
    RESOURCES = "resources"
    REPORT = "report"
    RUN = "run"
    EVIDENCE = "evidence"
    PLUGINS = "plugins"
    MODEL = "model"
    NEXT_PANE = "next_pane"
    PREVIOUS_PANE = "previous_pane"
    APPROVE = "approve"
    DENY = "deny"
    LAYOUT = "layout"
    SAVE_REPORT = "save_report"
    CLOSE_MODAL = "close_modal"
    COMMAND_PALETTE = "command_palette"
