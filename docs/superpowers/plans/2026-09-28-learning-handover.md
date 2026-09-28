# Learning handover implementation plan

User approved implementing the discussed design, then evaluating and continuing Swarm-Agent. Quality and delivery speed outrank minimizing weekly usage. No publishing or north-star changes.

## Design
Keep native Codex agents and the existing fresh-context supervisor. Add project-scoped indexed knowledge with evidence-backed proposals/promotion/rollback; reusable validation receipts based on content/tool/environment fingerprints; delivery-progress tracking and pause-after-shift. No Prime runtime installation, global memory writes, autonomous policy weakening, or new scheduler.

## Tasks and ownership
- [x] Sol knowledge worker: harness/knowledge.py + tests/test_knowledge.py only. Project context index and evidence-backed refinement lifecycle.
- [x] Sol validation worker: harness/verify.py + tests/test_verify.py only. Deterministic validations, immutable logs/receipts, conservative reuse.
- [x] Astra integrator: continuous.py delivery checks/drain/model effort; templates, workflow docs, exports and integration tests.
- [x] Review all modules, full regression and export check; commit framework and integrate local base branch.
- [ ] Assess paused Swarm-Agent: approvals, clean Git, existing artifacts and executable checks. Migrate workflow/knowledge/validation policy without changing product goals; snapshot and commit.
- [ ] If assessment passes, resume native continuous development with Astra and worker routing. Observe first delivered change and next fresh context, or capture a real blocking condition.

## Contracts
Validation config: version=1, groups object; group command argv, cwd, inputs exact relative files/directories, env_keys, tool_versions argv list, outputs optional, cache boolean, max_age_seconds, timeout_seconds. CLI: verify.py --workspace ROOT run GROUP [--force], status GROUP. Durable logs and JSON under docs/runs/validation, reuse only unchanged successful evidence; latest failure prevents older success reuse.
Knowledge: project knowledge/index.json, entries in knowledge/<slug>.md; candidate JSON under refinements/candidates; accepted version/history under refinements. CLI init, propose FILE, accept ID, rollback ID, context [--slug SLUG...]. Evidence references existing regular project files and hashes; stale evidence rejected. Protected paths and traversal rejected. Only memories/procedures/role guidance, never authority or approval edits. Slugs keyed by scope; next context loads index then selected content.
Progress: optional delivery config watches product/asset paths; detects repeated no-change shifts, instructs next context to reassess. If reassessment still yields no output, supervisor pauses with evidence, not endless tiny task subdivision. Normal progress restores counters. Explicit drain persists until resume; legacy stop remains immediate.

## Validation
Test cache invalidation on inputs/command/environment/tools, corrupt or missing evidence, failed latest run, timeout, output mutations and traversal. Test knowledge promotion/stale evidence/update/rollback and unrelated context exclusion. Test detached propagation, pause-after-shift, stagnation replan then bounded stop. Existing tests remain.
