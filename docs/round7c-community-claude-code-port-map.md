# Round 7C Community Claude-Code-Like Port Map

## Source Review And License

`D:\workspace\linux\claude-code-cli-master\claude-code-cli-master` contains a TypeScript/Ink terminal agent with `main.tsx`, `screens/REPL.tsx`, `commands/`, `components/`, `tools/`, `services/`, `keybindings/`, `plugins/`, `hooks/`, `context/`, and `state/`.

No top-level `LICENSE` file was found in the local copy during this round. Per project direction, OpsPilot uses it as a community product reference for behavior and architecture. OpsPilot does not copy private keys, prompts, unrelated branding, or product identity.

## How The Reference Starts

The reference app starts through a large CLI entrypoint in `main.tsx`. It parses flags, resolves mode/config/model/tool permissions, initializes background services, builds command/tool pools, and renders a persistent REPL screen.

OpsPilot mapping:

- `diag.cli.app.main()` now allows no subcommand and defaults to workbench.
- `diag workbench` explicitly starts the persistent terminal workspace.
- `scripts/opspilot.ps1`, `opspilot.cmd`, and `opspilot.sh` provide short launch commands.

## How It Keeps A Persistent Session

The reference keeps a REPL mounted and updates state as messages, tool uses, permissions, background tasks, and UI overlays change. It does not treat every user prompt as a one-shot process.

OpsPilot mapping:

- `diag/workbench/event_loop.py` owns the persistent `diag>` loop.
- `diag/workbench/session.py` records conversation and event history.
- `/exit` is the normal shutdown path; Ctrl+C writes a final transcript event before returning.

## How It Handles User Input

The reference routes input through a prompt component, recognizes slash commands, preserves history, and separates typed text from command execution.

OpsPilot mapping:

- `diag/workbench/input_adapter.py` uses `prompt_toolkit` when available and falls back to `input()`.
- Plain natural-language input updates the draft task and generates a plan, but does not execute tools.
- `/run` is the explicit execution boundary.

## How It Dispatches Slash Commands

The reference has a command registry with command metadata, filtering, local UI commands, and model-facing commands.

OpsPilot mapping:

- `diag/workbench/slash_commands.py` declares `/help`, `/plan`, `/run`, `/raw`, `/report`, `/resources`, `/model`, `/plugin`, `/config`, `/approve`, `/deny`, and `/exit`.
- `diag/workbench/command_router.py` parses and dispatches slash commands.
- `/` lists all commands; `/r` filters `/run`, `/raw`, `/report`, and `/resources`.

## How It Calls Tools

The reference assembles tools from built-ins, plugins, MCP, and permission filters, then runs them through permission-aware orchestration.

OpsPilot mapping:

- Workbench execution still calls `AgentLoop`.
- `AgentLoop` still builds the default `ToolRegistry`, runs `BeforeCommandHook`, evaluates `PermissionPolicy`, and executes through `CommandTool`.
- Workbench only supplies an approval provider for confirm-mode pause/resume.

## How It Displays UI Components

The reference uses Ink components for messages, prompt input, permission prompts, tool progress, status, and overlays.

OpsPilot mapping:

- `diag/workbench/live_renderer.py` renders a terminal workspace snapshot.
- `diag/workbench/panes/*` splits Conversation, Monitor, Plan, Evidence, Raw, Report, Resources, and StatusLine.
- Rich is optional; the fallback renderer remains usable in plain terminals.

## How It Handles Keybindings

The reference centralizes keybindings and routes global shortcuts separately from typed slash commands.

OpsPilot mapping:

- Round 7C provides command discovery and prefix filtering first.
- Keyboard-specific bindings remain a TODO for Textual/prompt-toolkit enhancement.

## How It Organizes Plugins

The reference loads built-in and marketplace plugins into command/tool surfaces.

OpsPilot mapping:

- Existing `diag.plugins.loader.PluginLoader` remains the plugin source.
- `/plugin` shows configured plugin metadata and does not add a new plugin API.

## How It Manages Session And Context

The reference uses shared app state, session IDs, context builders, and message history to keep the REPL coherent across turns.

OpsPilot mapping:

- `WorkbenchState` stores target, mode, draft input, current plan, dashboard view model, approval state, resources, and messages.
- `WorkbenchSession` stores a UTF-8 JSON transcript under `outputs/history/workbench/`.

## What Can Be Ported Versus Rewritten

Portable ideas:

- Persistent REPL as the product center.
- Slash command registry and prefix filtering.
- State-driven panes.
- Permission prompt queue as a first-class UI state.
- Tool progress events updating UI immediately.

Rewritten for OpsPilot:

- All implementation code.
- Runtime/tool execution integration.
- Permission policy wiring.
- Linux diagnosis panes and resource monitor.
- UTF-8 transcript/report handling.
