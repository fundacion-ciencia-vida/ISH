#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# -S proves that the public build uses only Python's standard library.
python3 -S scripts/build_site.py
python3 -S scripts/validate_site.py

printf 'Public site updated and validated in %s\n' "$ROOT"
