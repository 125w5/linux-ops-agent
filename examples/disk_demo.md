# Disk Diagnosis Demo

Run:

```bash
python -m diag diagnose --target localhost --task disk --demo
```

Expected behavior:

- A five-stage terminal workflow is printed.
- Read-only commands are checked before execution.
- Demo evidence shows high root filesystem usage.
- Markdown and JSON reports are written under `outputs/reports`.
- SQLite history is written under `outputs/history/diag.db`.
