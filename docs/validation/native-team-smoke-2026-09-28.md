# Native subagent smoke evidence — 2026-09-28

Read-only arithmetic test in a temporary empty Git repository. No game shift was started.
Binary: `/Applications/ChatGPT.app/Contents/Resources/codex`, `codex-cli 0.155.0-alpha.9`.
Parent model: `gpt-6-astra`, low effort for this bounded probe (production native shifts use high).
Native options: `agents.enabled=true`, `agents.max_concurrent_threads_per_session=2`,
`agents.default_subagent_model="gpt-6-sol"`, `agents.default_subagent_reasoning_effort="low"`.
Sandbox read-only, approval never. No `multi_agent_v2` override.

## Observed records

| Thread | Recorded model | Effort | Completed result |
|---|---|---|---|
| `01a0e5d8-ae54-7d73-afd2-9d8b28607536` | gpt-6-astra | low | Collected all three answers in one parent turn |
| `01a0e5d8-cd86-7531-a7df-f920c9693744` | gpt-6-sol | low | 17 × 19 = 323 |
| `01a0e5d8-e4aa-7cb2-aa97-639f7c6afd25` | gpt-5.6-terra | low | 23 × 29 = 667 |
| `01a0e5d9-01ee-7cd2-9951-6a5bf2f0071a` | gpt-6-luna | low | 31 × 37 = 1147 |

Checked the local rollout JSONL session_meta source.subagent.thread_spawn.parent_thread_id,
turn_context model/effort, and task_complete for each child. All three point to the same
parent. Parent tool records contain three spawn_agent calls with fork_turns=none and
explicit models, then wait_agent. Parent returned all results without another user prompt.
The exec JSONL stream contains native wait in_progress/completed and turn.completed.
This proves native child completion can continue a living CLI parent, without restarting it.

Raw runtime logs remain outside the repository; this receipt retains only test-specific IDs
and results, not full injected prompts or unrelated local configuration. Some unrelated
roblox-studio-mcp startup warnings occurred; that tool was not used or validated.

## Limits and replay

This is a capability smoke, not a coding quality, pricing or speed benchmark. It does not
prove artist/image-tool access, parallel file isolation, crash recovery, or termination of
worker-created independent process groups. Production high-effort Astra configuration and
mode propagation are checked by deterministic command/fixture tests, not by this low-effort probe.

To repeat when CLI/account capabilities change, launch one read-only Astra exec in a scratch
Git repository, request the same three fresh explicit-model children and native wait, then
verify actual child model metadata and parent IDs. Do not accept only the parent's self-report.
Ordinary framework regression uses `python3 -m unittest discover -s tests -v` and does not
consume live model calls. Repeating the live probe is unnecessary while this evidence applies.
