# Shared helpers for harness scripts. Source, don't execute.

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDIO_ROOT="$(cd "$HARNESS_DIR/.." && pwd)"
. "$HARNESS_DIR/config.sh"

STATE_DIR="$STUDIO_ROOT/.studio"
LOG_DIR="$STATE_DIR/logs"
SESSION_ENV="$STATE_DIR/session.env"   # exists <=> a shift is (or was) running
PAUSE_FILE="$STATE_DIR/PAUSE"
LAST_RESULT="$STATE_DIR/last-result"   # one-paragraph note injected into the next shift's prompt
mkdir -p "$LOG_DIR" "$STATE_DIR/daily"

export STUDIO_ROOT HANDOVER_FILE HANDOVER_MAX_CHARS

now() { date +%s; }
ts() { date '+%Y-%m-%d %H:%M:%S'; }
hhmm() { date -d "@$1" '+%H:%M' 2>/dev/null || date -r "$1" '+%H:%M'; }

log() { echo "[$(ts)] $*" >> "$LOG_DIR/harness.log"; [ -t 1 ] && echo "[harness] $*"; return 0; }

notify() {
  log "NOTIFY: $1"
  [ -n "$NOTIFY_CMD" ] && bash -c "$NOTIFY_CMD" _ "$1" >/dev/null 2>&1 || true
}

pid_alive() { [ -n "${1:-}" ] && kill -0 "$1" 2>/dev/null; }

# Loads session.env into the current shell (variables prefixed STUDIO_).
load_session() { [ -f "$SESSION_ENV" ] && . "$SESSION_ENV"; }

# Kill the shift's process groups (run-session and the agent under `timeout`).
kill_session_groups() {
  local sig="$1"
  for g in ${STUDIO_AGENT_PGID:-} ${STUDIO_PGID:-}; do
    kill "-$sig" -- "-$g" 2>/dev/null || true
  done
}

handover_status() {
  local f="$STUDIO_ROOT/$HANDOVER_FILE"
  [ -f "$f" ] || { echo "MISSING"; return; }
  sed -n 's/^STATUS:[[:space:]]*\([A-Z]*\).*/\1/p' "$f" | head -n1
}

today_count_file() { echo "$STATE_DIR/daily/$(date +%F)"; }
today_count() { cat "$(today_count_file)" 2>/dev/null || echo 0; }

# Render {{VAR}} placeholders in a template from the environment.
render_template() {
  python3 - "$1" <<'PY'
import os, re, sys
text = open(sys.argv[1], encoding="utf-8").read()
print(re.sub(r"\{\{(\w+)\}\}", lambda m: os.environ.get(m.group(1), m.group(0)), text))
PY
}
