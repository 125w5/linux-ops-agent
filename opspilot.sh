#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
export PYTHONPATH="$(pwd)"
if [ -n "${CONDA_PREFIX:-}" ] && [ -x "$CONDA_PREFIX/bin/python" ]; then
  export OPSPILOT_PYTHON="$CONDA_PREFIX/bin/python"
elif [ -z "${OPSPILOT_PYTHON:-}" ]; then
  export OPSPILOT_PYTHON="python3"
fi
BUN_CMD=""
if command -v bun >/dev/null 2>&1; then
  BUN_CMD="bun"
elif [ -x "$HOME/.bun/bin/bun" ]; then
  BUN_CMD="$HOME/.bun/bin/bun"
fi
if [ -n "$BUN_CMD" ] && [ -f "apps/opspilot-cli/src/main.tsx" ]; then
  "$BUN_CMD" run "apps/opspilot-cli/src/main.tsx" "$@"
  code=$?
  if [ "$code" -eq 0 ]; then
    exit 0
  fi
  echo "Bun frontend failed with exit code $code, falling back to Python workbench." >&2
fi
"$OPSPILOT_PYTHON" -m diag workbench --target localhost --mode readonly "$@"
