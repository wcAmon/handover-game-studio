#!/usr/bin/env python3
"""Claude Code hooks for harness-run shifts. No-ops outside a shift (STUDIO_SESSION_ID unset),
so interactive pre-production sessions are unaffected.

  session-start  inject the time budget (also re-injected after context compaction)
  post-tool      announce remaining time when a checkpoint is crossed
  stop           block ending the shift until handover.md passes check-handover (max 3 times)
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, ".studio")
SID = os.environ.get("STUDIO_SESSION_ID")
MAX_STOP_BLOCKS = 3


def env_int(name):
    return int(os.environ[name])


def time_left():
    return subprocess.run([os.path.join(ROOT, "harness/bin/time-left")], capture_output=True, text=True).stdout.strip()


def emit(event, context):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}, ensure_ascii=False))


def session_start(payload):
    extra = ""
    if payload.get("source") == "compact":
        extra = "\n（context 剛被壓縮：請重新讀 handover.md 的 NOW 任務，並以 git status / git diff 確認你做到哪。）"
    emit("SessionStart", f"[harness] 班次 {SID}（{os.environ.get('STUDIO_MODE', 'shift')}）時間預算：\n{time_left()}{extra}")


def post_tool(payload):
    start, soft, hard = (env_int(k) for k in ("STUDIO_START_EPOCH", "STUDIO_SOFT_DEADLINE_EPOCH", "STUDIO_HARD_DEADLINE_EPOCH"))
    now = time.time()
    checkpoints = sorted({t for t in range(start + 600, soft, 600)} | {soft, hard - 300, hard - 120, hard})
    passed = [t for t in checkpoints if t <= now]
    if not passed:
        return
    seen_file = os.path.join(STATE, f"time-notice-{SID}")
    last = int(open(seen_file).read() or 0) if os.path.exists(seen_file) else 0
    # Past the hard deadline, remind on every tool call; otherwise once per checkpoint.
    if passed[-1] <= last and now < hard:
        return
    with open(seen_file, "w") as f:
        f.write(str(passed[-1]))
    emit("PostToolUse", f"[harness 報時] {time_left()}")


def stop(payload):
    baseline = os.environ.get("STUDIO_BASELINE") if os.environ.get("STUDIO_MODE") == "shift" else None
    cmd = [os.path.join(ROOT, "harness/bin/check-handover")] + (["--baseline", baseline] if baseline else [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return
    count_file = os.path.join(STATE, f"stop-blocks-{SID}")
    count = int(open(count_file).read() or 0) if os.path.exists(count_file) else 0
    if count >= MAX_STOP_BLOCKS:
        return  # let it stop; run-session.sh will start a repair shift
    with open(count_file, "w") as f:
        f.write(str(count + 1))
    print(json.dumps({
        "decision": "block",
        "reason": "[harness 收班閘門] handover.md 尚未合格，請修正後再結束：\n"
                  + result.stdout.strip() + "\n" + time_left(),
    }, ensure_ascii=False))


def main():
    if not SID:
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    os.makedirs(STATE, exist_ok=True)
    {"session-start": session_start, "post-tool": post_tool, "stop": stop}[sys.argv[1]](payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
