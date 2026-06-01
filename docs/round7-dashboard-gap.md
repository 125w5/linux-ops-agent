# Round 7 Dashboard Gap

## Why `diag diagnose` currently feels like a script

The current default entrypoint runs the complete diagnosis loop and only exposes two kinds of CLI feedback:

- `diag.cli.output.stage()` prints fixed `[1/6]` milestones.
- `diag.ui.renderer.render_outcome()` prints the final summary after all tools, analysis, report writing, and history persistence finish.

The runtime already emits useful events such as `SessionStarted`, `PlanCreated`, `ToolStarted`, `ToolFinished`, `EvidenceAdded`, `ResourceUpdated`, and `ReportWritten`, but the default `diagnose` command does not turn those events into a persistent terminal workspace. As a result, users cannot see the active plan, running tool, evidence chain, resource pressure, risk state, or report path while the workflow is in progress.

## Terminal-agent elements seen in Cursor, Codex, and Claude Code style tools

The common product shape is not a web UI. It is a terminal workspace where the user can continuously see:

- Session context: target, task, mode, provider/model, risk.
- Live status: what is running, what is done, what was skipped or blocked.
- Tool activity: command/tool calls with permissions and outcomes.
- Evidence: facts collected from commands as they arrive.
- Resource/cost context: CPU, memory, disk, process pressure, command/AI usage.
- Raw output controls: raw command output exists but is folded unless requested.
- Report continuity: final Markdown/JSON artifacts are visible.
- Command discoverability: users can see how to enter chat, TUI, raw, or plain modes next.

## OpsPilot mapping

OpsPilot should map these concepts onto existing runtime events instead of adding new analyzers, providers, plugins, or command execution paths:

- Session context comes from `SessionStarted` and CLI args.
- Plan/tool calls come from `PlanCreated`, `ToolStarted`, `ToolFinished`, and approval events.
- Evidence comes from `EvidenceAdded`.
- Resource/cost context combines system samples with existing `ResourceUsage`.
- Report continuity comes from `ReportWritten`.
- Raw output remains available through `--view raw`; the dashboard shows a folded summary by default.
- Non-TTY and CI environments automatically use plain text output.

## Files changed in this round

- `diag/dashboard/view_model.py`: event-sourced state shared by diagnose and future TUI reuse.
- `diag/dashboard/renderers.py`: plain and Rich-compatible renderers.
- `diag/dashboard/live_dashboard.py`: live workspace runner around the existing `AgentLoop`.
- `diag/dashboard/system_monitor.py`: safe background sampler.
- `diag/dashboard/resource_sampler.py`: psutil-first resource sampling with standard-library/Linux fallback.
- `diag/dashboard/process_view.py`: process formatting helpers.
- `diag/dashboard/disk_view.py`: disk formatting helpers.
- `diag/cli/app.py`: default dashboard view selection, new `--view` values, `--no-live`, command hints.
- `diag/runtime/agent_loop.py`: event payload enrichment only; command execution remains routed through existing tool, policy, hook, and checker layers.
- `diag/utils/encoding.py`: UTF-8 stdout/stderr configuration.
- Tests under `tests/` for dashboard state, render output, monitor fallback, diagnose fallback, and UTF-8 JSON/text behavior.

## Non-copying statement

Claude-code-open-main was used only as a product-shape reference for concepts such as status lines, visible tool activity, permission/risk visibility, folded raw output, and command discoverability. No source code, prompts, internal names, or implementation details were copied into OpsPilot.
