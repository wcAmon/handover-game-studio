#!/usr/bin/env bash
# cron entry point (every 10 minutes). Idempotent: if a shift is running, do nothing;
# otherwise decide whether a new shift may start, and start it in the background.
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$STUDIO_ROOT"

# Only one tick at a time.
exec 9>"$STATE_DIR/tick.lock"
flock -n 9 || exit 0

if [ -f "$PAUSE_FILE" ]; then
  log "tick: paused ($(head -c 200 "$PAUSE_FILE"))"
  exit 0
fi

# --- Is a shift already running? -------------------------------------------
if [ -f "$SESSION_ENV" ]; then
  load_session
  if pid_alive "${STUDIO_PID:-}"; then
    abandon_at=$(( STUDIO_HARD_DEADLINE_EPOCH + KILL_GRACE_SECONDS + REPAIR_MINUTES * 60 + 600 ))
    if [ "$(now)" -lt "$abandon_at" ]; then
      log "tick: shift #$STUDIO_SESSION_NO running (pid $STUDIO_PID), nothing to do"
      exit 0
    fi
    log "tick: shift #$STUDIO_SESSION_NO is hung past $(hhmm "$abandon_at"); killing"
    kill_session_groups TERM; sleep 5; kill_session_groups KILL
    notify "Shift #$STUDIO_SESSION_NO hung and was killed. Check .studio/logs/."
  else
    log "tick: stale session.env for shift #${STUDIO_SESSION_NO:-?} (pid dead); cleaning up"
  fi
  echo "上一班 #${STUDIO_SESSION_NO:-?} 沒有正常收班（程序消失或卡死被終止）。工作區中可能有未完成的修改（已由 harness 以 wip commit 保存）；handover.md 可能未更新，請用 git log / git diff 確認實際進度後再開工。" > "$LAST_RESULT"
  rm -f "$SESSION_ENV"
fi

# --- May a new shift start? -------------------------------------------------
status="$(handover_status)"
case "$status" in
  ACTIVE) ;;
  MISSING)
    log "tick: no $HANDOVER_FILE yet — finish pre-production (/concept-art, /grill, /blueprint) first"
    exit 0 ;;
  *)
    # Notify once per status change, not every tick.
    stamp="$status $(stat -c %Y "$HANDOVER_FILE" 2>/dev/null || stat -f %m "$HANDOVER_FILE")"
    if [ "$(cat "$STATE_DIR/notified-status" 2>/dev/null)" != "$stamp" ]; then
      echo "$stamp" > "$STATE_DIR/notified-status"
      notify "handover STATUS is $status — shifts are on hold until a human sets it back to ACTIVE."
    fi
    log "tick: STATUS=$status, not starting"
    exit 0 ;;
esac

if [ "$MAX_SESSIONS_PER_DAY" -gt 0 ] && [ "$(today_count)" -ge "$MAX_SESSIONS_PER_DAY" ]; then
  log "tick: daily limit reached ($MAX_SESSIONS_PER_DAY)"
  exit 0
fi

# --- Start a shift, detached into its own session/process group. ---------------
log "tick: starting a new shift (agent=$AGENT)"
# 9>&- : the child must not inherit the tick lock, or later ticks could never check on it.
setsid nohup "$HARNESS_DIR/run-session.sh" >> "$LOG_DIR/harness.log" 2>&1 < /dev/null 9>&- &
exit 0
