# Native multi-model implementation plan

User authorized building the architecture, Astra orchestrator and Sol/Terra/Luna workers.
Existing game pause remains in force. Both installed CLI binaries are native ARM64;
use desktop bundled 0.155.0-alpha.9, not PATH 0.144.3. No global upgrade required.

## Final contract

- Codex native subagents handle intra-shift spawn, model selection, completion and wait.
- Existing continuous.py owns inter-shift fresh contexts, timeouts, failure limits and stop.
- Opt-in --team native fixes shift owner to Astra/high; worker default Sol/medium.
- Astra explicitly selects Sol/Terra/Luna with concise fresh contexts and records rationale.
- Four role prompt files, at most two children and one shared-workspace writer at a time.
- Parent verifies results and owns handover/commit; no automatic worktree/DAG/merge service.
- CLI doctor checks native feature and target-workspace role files without launching agents.
- No global config changes, no game restart, no publication.
- Behavioral model/path policy is documented honestly; no hard allowlist is claimed.

## Work

- [x] Inspect installed CLI and current official subagent docs.
- [x] Real scratch test: Astra spawns fresh Sol/Terra/Luna, native completion resumes parent.
- [x] Integrate native mode, model defaults, role prompts and readonly doctor.
- [x] Regression tests for mode propagation, fresh shifts, missing feature/roles, readonly doctor.
- [x] Review and repair target-workspace role validation.
- [x] Documentation, export route and handover.
- [x] Final export/regression checks: 17 tests and both handover checks passed; ready to commit.

## Design correction

The earlier draft proposed an external per-job scheduler. The user correctly asked about
built-in agents; direct CLI tests established the native mechanism, so that draft is not
part of the delivered framework. Its unintegrated prototype was preserved in temporary
storage for this session only. Existing repository tests were retained.
