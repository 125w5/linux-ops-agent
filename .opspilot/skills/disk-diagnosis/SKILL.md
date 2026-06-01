---
name: disk-diagnosis
description: Diagnose high disk usage with read-only evidence.
risk_max: safe_readonly
scenes: [disk]
---

# Disk Diagnosis Skill

Use read-only evidence first: filesystem usage, top-level directory size, large files, journal usage, and Docker disk usage when available.

Do not remove files, truncate logs, prune Docker, or vacuum journals. Suggestions must be previews only and must preserve the evidence chain.
