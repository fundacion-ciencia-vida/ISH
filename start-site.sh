#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${ISH_SITE_HOST:-0.0.0.0}"
PORT="${ISH_SITE_PORT:-8080}"

"$ROOT/update-site.sh"

printf 'Public site: http://127.0.0.1:%s/\n' "$PORT"
printf 'Listening on %s:%s (editor not required)\n' "$HOST" "$PORT"
exec python3 -S -m http.server "$PORT" --bind "$HOST" --directory "$ROOT"
