Process operations must be visual and approval-aware.

List/inspect/tree are safe-read actions.
SIGTERM requires an approval card in admin-confirm workflows.
SIGKILL is blocked unless a future explicit double-confirm policy is implemented.
Never allow killing root/system, PID 1, or OpsPilot's own process.
After a termination request, summarize what was sent and recommend rechecking process status after a short delay.
