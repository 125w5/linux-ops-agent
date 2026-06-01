---
name: nginx-service
description: Diagnose nginx service startup failures.
risk_max: safe_readonly
scenes: [service, service-failed]
---

# Nginx Service Skill

Collect service state, recent journal entries, and listening ports. Look for failed state, port conflicts, configuration errors, and permission errors.

Do not restart nginx, edit configuration, or kill port owners.
