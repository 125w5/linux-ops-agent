#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
BUN_CMD=""
if command -v bun >/dev/null 2>&1; then
  BUN_CMD="bun"
elif [ -x "$HOME/.bun/bin/bun" ]; then
  BUN_CMD="$HOME/.bun/bin/bun"
fi
if [ -n "$BUN_CMD" ] && [ -f "apps/opspilot-cli/src/main.tsx" ]; then
  if "$BUN_CMD" run "apps/opspilot-cli/src/main.tsx" "$@"; then
    exit 0
  fi
  printf '%s\n' "[opspilot] TypeScript frontend failed, falling back to Python workbench."
fi
python3 -m diag workbench --target localhost --mode demo "$@"
