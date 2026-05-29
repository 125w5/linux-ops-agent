# Architecture

OpsPilot-Linux is intentionally terminal-first. The system boundary is narrow:

```text
CLI -> planner -> safety checker -> executor -> analyzer -> report + SQLite history
```

The MVP uses deterministic runbooks and rule-based analysis. AI providers can be added behind a provider interface later, but command execution should remain constrained by the safety layer.
