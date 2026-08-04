#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV="$ROOT/.ish-editor/venv"

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r "$ROOT/editor/requirements.txt"
fi

if [ ! -f "$ROOT/editor/ui/dist/index.html" ]; then
  (cd "$ROOT/editor/ui" && npm ci && npm run build)
fi

exec "$VENV/bin/python" -m editor.launcher --workspace "$ROOT" "$@"
