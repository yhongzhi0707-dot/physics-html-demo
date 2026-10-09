#!/usr/bin/env bash
set -euo pipefail
rea_prefix="$(npm prefix --global)"
rea_bin="$rea_prefix/bin/rea"
if [[ ! -x "$rea_bin" ]]; then
  printf 'REA is not installed. Run the saved setup.sh first.\n' >&2
  exit 1
fi
exec "$rea_bin" "$@"
