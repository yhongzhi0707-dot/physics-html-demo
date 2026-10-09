#!/usr/bin/env bash
set -euo pipefail

# Paste this script into the cloud environment's setup-script setting.
# It installs only the official CLI and npm runtime dependencies.
# It never configures agents or installs Hopper/Ghidra/IDA/JADX/browsers.
command -v node >/dev/null
command -v npm >/dev/null
node <<'JS'
const version = process.versions.node;
const [major, minor] = version.split('.').map(Number);
const supported = !version.includes('-') && (
  (major === 22 && minor >= 19) ||
  (major === 24 && minor >= 11) ||
  major >= 26
);
if (!supported) {
  console.error(`Unsupported Node.js ${version}; REA requires ^22.19.0 || ^24.11.0 || >=26.0.0`);
  process.exit(1);
}
console.log(`Node.js ${version} satisfies REA's runtime requirement`);
JS
rea_prefix="$(npm prefix --global)"
rea_bin="$rea_prefix/bin/rea"
if [[ -x "$rea_bin" ]] && rea_existing_version="$("$rea_bin" --version 2>/dev/null)" && [[ "$rea_existing_version" == "6.2.0" ]]; then
  printf 'REA %s is already available; skipping npm installation.\n' "$rea_existing_version"
else
  npm install --global rea-agents@6.2.0 --no-audit --no-fund
fi
rea_version="$("$rea_bin" --version)"
if [[ "$rea_version" != "6.2.0" ]]; then
  printf 'Unexpected REA version: %s\n' "$rea_version" >&2
  exit 1
fi
printf 'REA %s installed at %s\n' "$rea_version" "$rea_bin"
case ":${PATH:-}:" in
  *":$rea_prefix/bin:"*) printf 'rea is available on PATH.\n' ;;
  *)
    printf 'The global npm bin directory is absent from PATH. Configure %s/bin in the cloud environment PATH setting.\n' "$rea_prefix" >&2
    printf 'Setup-shell exports do not persist into the agent phase; use the absolute CLI path until PATH is configured.\n' >&2
    exit 1
    ;;
esac
