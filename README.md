# OpsPilot-Linux

OpsPilot-Linux is a terminal-first Linux operations diagnosis assistant. It turns a short fault description or fixed task into a safe, auditable diagnosis workflow:

```text
intent -> diagnosis plan -> safety check -> command execution -> evidence analysis -> report
```

The current runtime supports disk, CPU, service-failure, and SSH-failure demo diagnostics:

```bash
python -m diag diagnose --target localhost --task disk
python -m diag diagnose --target localhost --task disk --demo
python -m diag diagnose --target localhost --task cpu --demo
python -m diag diagnose --target localhost --task service --service nginx --demo
python -m diag diagnose --target localhost --task ssh-failure --demo
python -m diag history
python -m diag report --last
```

## Why This Shape

- AI should help understand and explain, but it should not freely execute shell commands.
- Commands go through a safety checker before execution.
- Every conclusion is backed by an evidence item.
- Reports are written as Markdown and JSON so the diagnosis can be reviewed later.

## Project Layout

```text
diag/
  cli/          terminal commands and output
  planner/      task intent and runbook planning
  runtime/      session, transcript, and agent loop
  tools/        tool specs and registry
  hooks/        before/after command lifecycle
  permissions/  permission modes and policy
  safety/       command risk classification
  executor/     local shell execution
  analyzers/    rule-based evidence extraction
  reports/      Markdown and JSON reports
  storage/      SQLite history
  tooldocs/     local command help/man indexing sandbox
```

## Notes

The default mode executes read-only commands on the local machine. On non-Linux systems, use `--demo` to replay fixture-like sample output.

ToolDocs indexes local command documentation without networking:

```bash
python -m diag docs index --commands df,du,ps,ss,journalctl,systemctl
python -m diag docs show --command journalctl
python -m diag docs profile --command ss
python -m diag docs suggest --scene service-failed
```
