# Harness configuration. Sourced by every harness script.
# Override any value with an environment variable, or create harness/config.local.sh (gitignored).

# Which agent runs production shifts: claude | codex | mock (mock = dry run, no tokens)
AGENT="${AGENT:-claude}"

# Shift length. Soft deadline = start + SESSION_MINUTES - WRAPUP_MINUTES (agent starts handing over).
# Hard deadline = start + SESSION_MINUTES. The process group is killed KILL_GRACE_SECONDS later.
SESSION_MINUTES="${SESSION_MINUTES:-45}"
WRAPUP_MINUTES="${WRAPUP_MINUTES:-8}"
KILL_GRACE_SECONDS="${KILL_GRACE_SECONDS:-300}"
REPAIR_MINUTES="${REPAIR_MINUTES:-5}"

# Handover constraints
HANDOVER_FILE="${HANDOVER_FILE:-handover.md}"
HANDOVER_MAX_CHARS="${HANDOVER_MAX_CHARS:-8000}"

# Spending guard: max shifts started per calendar day (0 = unlimited)
MAX_SESSIONS_PER_DAY="${MAX_SESSIONS_PER_DAY:-24}"

# Agent command lines. Unattended shifts need permissions pre-granted:
# run them inside a VM/container you are willing to let the agent control.
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
CLAUDE_ARGS="${CLAUDE_ARGS:---dangerously-skip-permissions --output-format stream-json --verbose}"
CODEX_BIN="${CODEX_BIN:-codex}"
CODEX_ARGS="${CODEX_ARGS:---full-auto}"

# Git: commit after every shift; push if GIT_PUSH=1
GIT_COMMIT="${GIT_COMMIT:-1}"
GIT_PUSH="${GIT_PUSH:-0}"
GIT_REMOTE="${GIT_REMOTE:-origin}"

# Optional notification command; receives the message as $1.
# e.g. NOTIFY_CMD='curl -s -d "$1" ntfy.sh/my-game-studio'
NOTIFY_CMD="${NOTIFY_CMD:-}"

# cron runs with a minimal PATH; add where claude/codex/node live.
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

[ -f "$(dirname "${BASH_SOURCE[0]}")/config.local.sh" ] && . "$(dirname "${BASH_SOURCE[0]}")/config.local.sh"
