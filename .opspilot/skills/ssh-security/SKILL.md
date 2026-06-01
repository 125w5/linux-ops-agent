---
name: ssh-security
description: Analyze SSH authentication failures from local logs.
risk_max: safe_readonly
scenes: [ssh-failure]
---

# SSH Security Skill

Count failed passwords, invalid users, source IPs, and targeted usernames. Treat remediation as advisory only.

Do not edit sshd configuration, block IPs, restart services, or write firewall rules.
