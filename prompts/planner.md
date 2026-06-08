Planner contract:
- Return only tool_calls and actions from registered tools.
- Do not output shell commands.
- Prefer safe-read evidence collection first.
- Keep the initial plan skeleton short.
- Dangerous work must be represented as approval-gated actions, not execution.
