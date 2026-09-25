#!/usr/bin/env bash
# One shift, start to finish:
#   claim slot → salvage leftovers → snapshot handover → run agent under a hard timeout
#   → gate the handover (repair shift if needed) → commit/push → note for the next shift.
# Usually launched by tick.sh; `harness/studio run-now [--foreground]` calls it directly.
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$STUDIO_ROOT"

FOREGROUND=0
[ "${1:-}" = "--foreground" ] && FOREGROUND=1

case "$AGENT" in
  claude) AGENT_BIN="$CLAUDE_BIN" ;;
  codex)  AGENT_BIN="$CODEX_BIN" ;;
  mock)   AGENT_BIN="python3" ;;
  *) echo "unknown AGENT=$AGENT" >&2; exit 2 ;;
esac
if ! command -v "$AGENT_BIN" >/dev/null 2>&1; then
  echo "agent binary '$AGENT_BIN' not found on PATH ($PATH)" > "$PAUSE_FILE"
  notify "Studio paused: '$AGENT_BIN' not found. Fix PATH in harness/config.sh, then: harness/studio resume"
  exit 1
fi

# --- Claim the shift slot (noclobber makes this atomic) ------------------------
if [ -f "$SESSION_ENV" ]; then
  load_session
  if pid_alive "${STUDIO_PID:-}"; then
    echo "shift #$STUDIO_SESSION_NO is already running (pid $STUDIO_PID)" >&2; exit 1
  fi
  rm -f "$SESSION_ENV"
fi

SESSION_NO=$(( $(cat "$STATE_DIR/counter" 2>/dev/null || echo 0) + 1 ))
SESSION_TAG=$(printf '%04d' "$SESSION_NO")
START=$(now)
SOFT=$(( START + (SESSION_MINUTES - WRAPUP_MINUTES) * 60 ))
HARD=$(( START + SESSION_MINUTES * 60 ))
PGID=$(ps -o pgid= -p $$ | tr -d ' ')

if ! ( set -C; cat > "$SESSION_ENV" ) 2>/dev/null <<EOF
STUDIO_SESSION_NO=$SESSION_NO
STUDIO_SESSION_ID=$(date +%Y%m%d-%H%M%S)-$SESSION_TAG
STUDIO_PID=$$
STUDIO_PGID=$PGID
STUDIO_AGENT=$AGENT
STUDIO_START_EPOCH=$START
STUDIO_SOFT_DEADLINE_EPOCH=$SOFT
STUDIO_HARD_DEADLINE_EPOCH=$HARD
EOF
then
  echo "another shift claimed the slot first" >&2; exit 1
fi
trap 'rm -f "$SESSION_ENV"' EXIT
echo "$SESSION_NO" > "$STATE_DIR/counter"
echo $(( $(today_count) + 1 )) > "$(today_count_file)"

load_session
export STUDIO_SESSION_NO STUDIO_SESSION_ID STUDIO_START_EPOCH STUDIO_SOFT_DEADLINE_EPOCH STUDIO_HARD_DEADLINE_EPOCH
LOGF="$LOG_DIR/shift-$SESSION_TAG.log"
log "shift #$SESSION_TAG start (agent=$AGENT, soft $(hhmm "$SOFT"), hard $(hhmm "$HARD"), log $LOGF)"

# --- Git helpers ----------------------------------------------------------------
IS_GIT=0; git rev-parse --is-inside-work-tree >/dev/null 2>&1 && IS_GIT=1
GITC=()
if [ "$IS_GIT" = 1 ] && ! git config user.email >/dev/null; then
  GITC=(-c user.name="Handover Studio" -c user.email="studio@localhost")
fi
git_commit_all() {
  [ "$IS_GIT" = 1 ] && [ "$GIT_COMMIT" = 1 ] || return 0
  [ -n "$(git status --porcelain)" ] || return 0
  git add -A && git "${GITC[@]}" commit -q -m "$1" && log "committed: $1"
}

# Leftovers from a shift that died without cleaning up: keep them, never discard work.
git_commit_all "wip: salvage uncommitted changes found before shift #$SESSION_TAG"

# --- Prompt context -----------------------------------------------------------------
BASELINE="$STATE_DIR/handover.before.md"
cp "$HANDOVER_FILE" "$BASELINE"
export STUDIO_BASELINE="$BASELINE"
export SESSION_MINUTES WRAPUP_MINUTES REPAIR_MINUTES
export START_HHMM="$(hhmm "$START")" SOFT_HHMM="$(hhmm "$SOFT")" HARD_HHMM="$(hhmm "$HARD")"
export PREVIOUS_RESULT="$(cat "$LAST_RESULT" 2>/dev/null || echo "（無紀錄：這可能是第一班。）")"
if [ "$AGENT" = claude ]; then
  export TIME_NOTE="harness 會在你使用工具時自動注入剩餘時間提醒；也可隨時執行 harness/bin/time-left。"
else
  export TIME_NOTE="你不會收到自動時間提醒：每完成一個步驟（或至少每 10 分鐘）就執行一次 harness/bin/time-left，結束前執行 harness/bin/check-handover。"
fi

# run_agent <prompt> <minutes> — runs the agent under a hard timeout; returns its exit code.
run_agent() {
  local prompt="$1" minutes="$2" cmd pid
  case "$AGENT" in
    claude) cmd=("$CLAUDE_BIN" -p "$prompt" $CLAUDE_ARGS) ;;
    codex)  cmd=("$CODEX_BIN" exec $CODEX_ARGS "$prompt") ;;
    mock)   cmd=(python3 "$HARNESS_DIR/bin/mock-agent") ;;
  esac
  echo "===== $(ts) $STUDIO_MODE ($minutes min) =====" >> "$LOGF"
  # `timeout` puts itself in its own process group and signals the whole group,
  # so dev servers etc. started by the agent die with it.
  if [ "$FOREGROUND" = 1 ]; then
    timeout --kill-after="${KILL_GRACE_SECONDS}s" "${minutes}m" "${cmd[@]}" < /dev/null > >(tee -a "$LOGF") 2>&1 &
  else
    timeout --kill-after="${KILL_GRACE_SECONDS}s" "${minutes}m" "${cmd[@]}" < /dev/null >> "$LOGF" 2>&1 &
  fi
  pid=$!
  echo "STUDIO_AGENT_PGID=$pid" >> "$SESSION_ENV"
  wait "$pid"
}

check_handover() {
  python3 "$HARNESS_DIR/bin/check-handover" --baseline "$BASELINE" 2>&1
}

# --- The shift -----------------------------------------------------------------------
export STUDIO_MODE=shift
run_agent "$(render_template "$HARNESS_DIR/prompts/shift.md")" "$SESSION_MINUTES"
rc=$?
TIMED_OUT=0; { [ $rc = 124 ] || [ $rc = 137 ]; } && TIMED_OUT=1
DURATION=$(( ($(now) - START + 59) / 60 ))
log "shift #$SESSION_TAG agent exited rc=$rc after ${DURATION}m (timed_out=$TIMED_OUT)"

# --- Handover gate ---------------------------------------------------------------------
REPAIRED=0
if ! errors="$(check_handover)"; then
  FIRST_ERRORS="$errors"
  log "handover check failed: $errors"
  # Commit the shift's work first so the repair shift can't lose it.
  git_commit_all "wip: shift #$SESSION_TAG ($AGENT, ${DURATION}m) before handover repair"
  export STUDIO_MODE=repair CHECK_ERRORS="$errors"
  export STUDIO_SOFT_DEADLINE_EPOCH=$(( $(now) + (REPAIR_MINUTES - 1) * 60 ))
  export STUDIO_HARD_DEADLINE_EPOCH=$(( $(now) + REPAIR_MINUTES * 60 ))
  run_agent "$(render_template "$HARNESS_DIR/prompts/repair.md")" "$REPAIR_MINUTES"
  if errors="$(check_handover)"; then
    REPAIRED=1
  else
    echo "shift #$SESSION_TAG: handover still invalid after repair: $errors" > "$PAUSE_FILE"
    notify "Studio paused: handover invalid after repair (shift #$SESSION_TAG). Fix $HANDOVER_FILE, then: harness/studio resume"
  fi
fi

# --- Commit & note for the next shift ---------------------------------------------------
summary="$(grep -m1 -E "^- *#0*$SESSION_NO\b" "$HANDOVER_FILE" | sed -E 's/^- *//' | cut -c1-120)"
[ -n "$summary" ] || summary="#$SESSION_TAG"
prefix="shift"; [ "$TIMED_OUT" = 1 ] && prefix="wip(timeout)"
git_commit_all "$prefix $summary [$AGENT ${DURATION}m]"
if [ "$IS_GIT" = 1 ] && [ "$GIT_PUSH" = 1 ]; then
  git push -q "$GIT_REMOTE" HEAD >> "$LOGF" 2>&1 || log "git push failed (see $LOGF)"
fi

if [ "$TIMED_OUT" = 1 ]; then
  note="上一班 #$SESSION_TAG 在硬截止時被強制中止（沒有主動收班）。它的殘留修改已由 harness commit 保存；請先用 git log -3 / git show --stat 確認實際進度與 handover 是否一致，並考慮把任務切得更小。"
else
  note="上一班 #$SESSION_TAG 正常交班（用時 ${DURATION} 分鐘）。"
fi
[ "$REPAIRED" = 1 ] && note="$note 注意：它交出的 handover 不合格（$(echo "$FIRST_ERRORS" | grep -m3 '✗' | tr '\n' ' ')），已由修復班修正，請特別檢查交班內容是否完整。"
echo "$note" > "$LAST_RESULT"
log "shift #$SESSION_TAG done: timed_out=$TIMED_OUT repaired=$REPAIRED status=$(handover_status)"
