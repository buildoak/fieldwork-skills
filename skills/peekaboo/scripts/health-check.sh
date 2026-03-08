#!/bin/bash
set -euo pipefail

PEEKABOO_BIN="${PEEKABOO_BIN:-$(command -v peekaboo || true)}"

if ! command -v jq >/dev/null 2>&1; then
  echo '{"overall_status":"unhealthy","error":"jq_not_found"}'
  exit 1
fi

if [ -z "${PEEKABOO_BIN}" ] || [ ! -x "$PEEKABOO_BIN" ]; then
  echo '{"overall_status":"unhealthy","error":"peekaboo_not_found"}'
  exit 1
fi

json='{}'
putb(){ json=$(jq --arg k "$1" --argjson v "$2" '. + {($k):$v}' <<<"$json"); }
puts(){ json=$(jq --arg k "$1" --arg v "$2" '. + {($k):$v}' <<<"$json"); }
putn(){ json=$(jq --arg k "$1" --argjson v "$2" '. + {($k):$v}' <<<"$json"); }

putb cli_exists true
puts cli_version "$($PEEKABOO_BIN --version 2>/dev/null || echo unknown)"

if perms=$($PEEKABOO_BIN list permissions --json 2>/dev/null); then
  putb permissions_check_success true
  perm_src='(.permissions // .data.permissions // [])'
  puts accessibility_granted "$(jq -r "$perm_src | any(.name==\"Accessibility\" and .isGranted==true)" <<<"$perms")"
  puts screen_recording_granted "$(jq -r "$perm_src | any(.name==\"Screen Recording\" and .isGranted==true)" <<<"$perms")"
else
  putb permissions_check_success false
  puts accessibility_granted false
  puts screen_recording_granted false
fi

if ax=$($PEEKABOO_BIN list apps --json 2>/dev/null); then
  app_count=$(jq '.data.applications | length // 0' <<<"$ax")
  putb ax_test_success true
  putn ax_test_elements "$app_count"
else
  putb ax_test_success false
  putn ax_test_elements 0
fi

# Peekaboo daemon check
if pgrep -f "peekaboo daemon" >/dev/null 2>&1; then
  putb daemon_running true
else
  putb daemon_running false
fi

# Display count — HDMI dummy plug check for headless Mac Mini
display_count=$(system_profiler SPDisplaysDataType 2>/dev/null | grep -c "Resolution:" || echo 0)
putn display_count "$display_count"
if [ "$display_count" -gt 0 ]; then
  putb display_connected true
else
  putb display_connected false
fi

# UI-TARS vision server (optional — warning only, not required for health)
if curl -sf http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then
  putb ui_tars_available true
else
  putb ui_tars_available false
fi

# Screenshot dir
mkdir -p "${TMPDIR:-/tmp}/peekaboo" 2>/dev/null || true

if [ "$(jq -r '.cli_exists' <<<"$json")" = true ] && [ "$(jq -r '.accessibility_granted' <<<"$json")" = true ] && [ "$(jq -r '.ax_test_success' <<<"$json")" = true ]; then
  puts overall_status healthy
  code=0
else
  puts overall_status unhealthy
  code=1
fi

# Warnings (non-fatal)
warnings='[]'
if [ "$(jq -r '.daemon_running' <<<"$json")" = false ]; then
  warnings=$(jq '. + ["peekaboo daemon not running - start with: peekaboo daemon run --mode manual &"]' <<<"$warnings")
fi
if [ "$(jq -r '.display_connected' <<<"$json")" = false ]; then
  warnings=$(jq '. + ["no display detected - HDMI dummy plug may be disconnected"]' <<<"$warnings")
fi
if [ "$(jq -r '.ui_tars_available' <<<"$json")" = false ]; then
  warnings=$(jq '. + ["UI-TARS server not running on :8080 - may cause timeouts in complex apps"]' <<<"$warnings")
fi
json=$(jq --argjson w "$warnings" '. + {warnings: $w}' <<<"$json")

echo "$json"
exit "$code"
