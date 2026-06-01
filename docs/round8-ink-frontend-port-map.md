# Round 8 Ink Frontend Port Map

## Reference Structure Learned

The local `claude-code-cli-master` is organized as a terminal product rather than a single command script:

- `main.tsx`: parses CLI flags, initializes state/config/services, assembles tools and commands, then renders the persistent REPL.
- `commands/`: slash command registry and command-specific screens/actions.
- `components/`: reusable Ink UI pieces for messages, prompt input, permission prompts, status, tool progress, and dialogs.
- `screens/`: high-level screens such as REPL, resume, and doctor.
- `tools/`: tool definitions plus permission-aware execution surfaces.
- `services/`: API, MCP, session, compacting, analytics, plugin, and background services.
- `plugins/`: bundled/plugin metadata and loading paths.
- `keybindings/`: shortcut schema, defaults, parser, resolver, and handlers.
- `context/` and `state/`: shared app state and provider-style context wiring.

No top-level `LICENSE` file was found in the local copy during this round. OpsPilot therefore ports product structure and behavior, while keeping implementation code, prompts, branding, and secrets separate.

## OpsPilot Migration Shape

Keep in Python:

- Linux diagnosis engine.
- ToolRegistry, PermissionPolicy, BeforeCommandHook, command_checker.
- Analyzers, reports, resource sampling, plugins, providers.
- Batch CLI compatibility: `diagnose`, `chat`, `tui`, `health`.

Move to TypeScript/Ink frontend:

- Persistent app shell.
- Conversation pane, input box, command palette, status line.
- Plan/tool/evidence/raw/report/resources panes.
- Model/config/plugin screens.
- Keybinding registry and command filtering.

Bridge:

- JSON-RPC over stdio, one JSON line per message.
- Frontend never executes shell.
- Python engine emits structured events for tool progress, evidence, resources, approvals, and reports.

## OpsPilot File Mapping

- `apps/opspilot-cli/src/main.tsx`: Commander entrypoint.
- `apps/opspilot-cli/src/app.tsx`: Ink root component.
- `apps/opspilot-cli/src/services/engineClient.ts`: JSON-RPC stdio client.
- `diag/engine/rpc_server.py`: Python JSON-RPC loop.
- `diag/engine/methods.py`: safe method dispatch into existing runtime.
- `diag/engine/protocol.py`: request/response/event message helpers.
- `diag/engine/session_manager.py`: session state, evidence, plan, model/config state.

## Do Not Copy

- Private keys, secrets, or environment values.
- Claude/third-party prompts.
- Product branding unrelated to OpsPilot.
- Direct shell execution in the frontend.
