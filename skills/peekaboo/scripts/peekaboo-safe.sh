#!/bin/bash
# peekaboo-safe.sh — Timeout-guarded peekaboo wrapper
# Prevents zombie processes from blocking the daemon bridge socket.
#
# Usage: peekaboo-safe.sh <peekaboo-subcommand> [args...]
# Example: peekaboo-safe.sh see --app Safari --json
#          peekaboo-safe.sh image --mode screen
#          peekaboo-safe.sh click --coords 300,200
#
# Environment:
#   PEEKABOO_TIMEOUT  — per-command timeout in seconds (default: 30)
#   PEEKABOO_MAX_AGE  — kill see/image processes older than this (seconds, default: 60)
#   PEEKABOO_BIN      — path to peekaboo binary (default: in PATH)

set -euo pipefail

PEEKABOO_BIN="${PEEKABOO_BIN:-$(command -v peekaboo || true)}"
PEEKABOO_TIMEOUT="${PEEKABOO_TIMEOUT:-30}"
PEEKABOO_MAX_AGE="${PEEKABOO_MAX_AGE:-60}"

log() { echo "[peekaboo-safe $(date +%H:%M:%S)] $*" >&2; }

if [ -z "${PEEKABOO_BIN}" ] || [ ! -x "$PEEKABOO_BIN" ]; then
  echo "peekaboo executable not found. Set PEEKABOO_BIN or install peekaboo in PATH." >&2
  exit 127
fi

# --- Pre-flight: kill stale see/image processes ---
preflight_cleanup() {
  local killed=0
  while IFS= read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    elapsed=$(echo "$line" | awk '{print $2}')
    cmd=$(echo "$line" | cut -d' ' -f3-)

    # Parse elapsed time (MM:SS or HH:MM:SS)
    local seconds=0
    if [[ "$elapsed" == *-* ]]; then
      seconds=999999  # days — definitely stale
    elif [[ "$elapsed" == *:*:* ]]; then
      IFS=: read -r h m s <<< "$elapsed"
      seconds=$(( 10#$h * 3600 + 10#$m * 60 + 10#$s ))
    elif [[ "$elapsed" == *:* ]]; then
      IFS=: read -r m s <<< "$elapsed"
      seconds=$(( 10#$m * 60 + 10#$s ))
    fi

    if (( seconds > PEEKABOO_MAX_AGE )); then
      log "KILL stale (${seconds}s): PID=$pid $cmd"
      kill -9 "$pid" 2>/dev/null && ((killed++)) || true
    fi
  done < <(ps -eo pid,etime,command 2>/dev/null | grep -E "peekaboo (see|image)" | grep -v grep | grep -v "peekaboo-safe")

  if (( killed > 0 )); then
    log "Pre-flight: killed $killed stale process(es)"
    sleep 0.5  # let bridge socket recover
  fi
}

# --- Execute with timeout ---
run_with_timeout() {
  "$PEEKABOO_BIN" "$@" &
  local child_pid=$!
  local start_time=$SECONDS

  # Wait with timeout
  local elapsed=0
  while kill -0 "$child_pid" 2>/dev/null; do
    elapsed=$(( SECONDS - start_time ))
    if (( elapsed >= PEEKABOO_TIMEOUT )); then
      log "TIMEOUT (${PEEKABOO_TIMEOUT}s): peekaboo $*"
      kill -9 "$child_pid" 2>/dev/null || true
      wait "$child_pid" 2>/dev/null || true
      return 124  # same as timeout(1) exit code
    fi
    sleep 0.2
  done

  wait "$child_pid"
  return $?
}

# --- Post-flight: kill any orphaned see/image from THIS run ---
postflight_cleanup() {
  local killed=0
  while IFS= read -r pid; do
    # Only kill very fresh orphans (< 5 seconds old would be from us)
    local etime
    etime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
    if [[ "$etime" =~ ^[0-9]+:[0-9]+$ ]]; then
      IFS=: read -r m s <<< "$etime"
      if (( 10#$m == 0 && 10#$s < 5 )); then
        log "POST-KILL orphan: PID=$pid"
        kill -9 "$pid" 2>/dev/null && ((killed++)) || true
      fi
    fi
  done < <(pgrep -f "peekaboo (see|image)" 2>/dev/null || true)

  if (( killed > 0 )); then
    log "Post-flight: killed $killed orphaned process(es)"
  fi
}

# --- Main ---
if [ $# -eq 0 ]; then
  echo "Usage: peekaboo-safe.sh <subcommand> [args...]" >&2
  exit 1
fi

preflight_cleanup
run_with_timeout "$@"
exit_code=$?
postflight_cleanup

if (( exit_code == 124 )); then
  log "Command timed out - bridge socket may need daemon restart"
fi

exit $exit_code
