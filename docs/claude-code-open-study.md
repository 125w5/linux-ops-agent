# Claude-code-open Architecture Study

This note records architecture ideas studied from `Claude-code-open-main` for OpsPilot-Linux Round 2. It intentionally avoids copying source code, prompts, variable names, or implementation details from the reference project. Only common, reusable agent architecture patterns are captured.

## CLI Entry Structure

The reference CLI separates a very small bootstrap entrypoint from the heavier runtime. Fast paths such as version/help are handled before loading the full application. More complex commands are routed into dedicated command modules.

Reusable idea for OpsPilot-Linux:

- Keep `python -m diag` as the stable entrypoint.
- Let `diag/cli/app.py` parse terminal commands, then delegate diagnosis work to a runtime layer.
- Avoid putting execution, permission, analysis, report writing, and history storage directly inside CLI handlers.

## Agent Loop Idea

The reference project treats an agent turn as a controlled loop around messages, tools, permissions, hook execution, and session state. Tool use is not a raw function call; it is an eventful lifecycle.

Reusable idea for OpsPilot-Linux:

- Model one diagnosis as a session.
- Make diagnosis execution flow through a runtime loop:
  `session -> plan -> tool calls -> before hooks -> command execution -> after hooks -> analysis -> reports -> transcript`.
- Keep disk, CPU, service, and SSH diagnosis under the same runtime path.

## Tool Registry And Tool Spec Idea

The reference project centralizes tools behind typed definitions and a merged tool list. Tools expose metadata and input schemas instead of being scattered ad hoc calls.

Reusable idea for OpsPilot-Linux:

- Add `ToolSpec` with `name`, `description`, `command_template`, `risk`, and `scenes`.
- Register diagnosis commands by scene.
- Let the planner produce tool calls from specs, then render the final shell command only at the last responsible moment.

## Permission And Approval Idea

The reference project treats permission as a first-class decision, with modes, rules, prompts, and denial paths. Shell tools receive extra safety handling before execution.

Reusable idea for OpsPilot-Linux:

- Keep `diag/safety/command_checker.py` as the final shell command gate.
- Add permission modes: `demo`, `readonly`, `confirm`, `fault-lab`, and `blocked`.
- Deny dangerous commands by default.
- Require confirmation for low-risk operations, while the MVP remains non-destructive.

## Hook Lifecycle Idea

The reference project exposes pre-tool and post-tool lifecycle points. Hooks can add context, block, or report errors, and hook failure is surfaced.

Reusable idea for OpsPilot-Linux:

- Add `BeforeCommand` and `AfterCommand` hooks.
- `BeforeCommand` must call the safety checker through the permission policy.
- `AfterCommand` records command results into the transcript/audit trail.
- Hook errors should produce clear runtime errors instead of disappearing silently.

## Memory And Instruction File Idea

The reference project loads persistent instruction/memory files from layered locations, applies size limits, supports include-like composition, and deduplicates session injection.

Reusable idea for OpsPilot-Linux:

- Keep this as a future direction, not part of Round 2 implementation.
- OpsPilot can later load local runbooks, safety policy, and diagnosis notes as bounded instruction context.
- Any future memory loading should be size-limited, explicit, and auditable.

## Transcript And Session Record Idea

The reference project treats conversation history and session events as durable records. Tool outputs and session events can be replayed, searched, or summarized later.

Reusable idea for OpsPilot-Linux:

- Generate a `session_id` for every diagnosis.
- Persist a JSON transcript containing user input, plan, commands, results, evidence, and report paths.
- Continue writing SQLite history for quick terminal listing.

## Borrowable Points For OpsPilot-Linux

- Thin CLI, thick runtime.
- Stable tool registry instead of scattered shell command strings.
- Permission mode as explicit runtime state.
- Command lifecycle hooks.
- Transcript-first diagnosis audit.
- Report generation as the final product of a session.

## What Must Not Be Copied

- No source files, prompts, schemas, variable names, or internal implementation details from the reference project.
- No Web UI or remote-control features.
- No automatic repair or write/destructive command execution.
- No bypass mode equivalent to unrestricted permissions.
- No bypass of `diag/safety/command_checker.py`.
- No hidden network-based documentation collection.
