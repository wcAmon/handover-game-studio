# Native finisher routing validation — 2026-09-28

Framework base: `fd4b538`. Scope: native shift role routing and documentation only; no game workspace mutation, scheduler, publishing, or push.

The native branch of `continuous.prompt()` now opens with Astra's orchestration duties instead of the single-agent command to test, update handover, and commit. `native_team.ROLES` requires a fifth role file, `finisher.md`. Prompt guidance routes stable diff review to an independent Sol reviewer, final validation and shift close to a Sol finisher, and product repairs back to a coder. The soft cutoff stops new product work while allowing necessary review and finalization. The non-native prompt and supervisor's deterministic checker, rescue commit, and fresh-context loop remain in place.

Verification performed in this framework worktree:

- `python3 -m unittest discover -s tests -v`: 57 passed, 0 failed.
- `harness/bin/check-handover`: passed (2,281 / 8,000 characters).
- `git diff --check`: passed.
- `python3 -m py_compile harness/native_team.py harness/continuous.py`: passed.
- `python3 harness/continuous.py doctor --codex /Applications/ChatGPT.app/Contents/Resources/codex`: passed; local CLI `0.155.0-alpha.9` reports native multi-agent available and five role files present.
- Export tests confirm `finisher.md` and native role guidance are included in blank and example workspaces.

These are fixture and static policy checks. They do not prove a live native shift will follow the routing, that a Sol finisher completed a product review, or that any game artifact passed visual acceptance. A separate Sol review of this framework commit remains required before integration.

## Independent Sol review follow-up

Review of `69af61f` requested two bounded corrections. The reviewer and finisher role contracts now require the reviewed base SHA, a reproducible working-diff fingerprint, reviewed paths, findings or explicit no-findings, coder repair and re-review results. `native_team.py fingerprint --base BASE_SHA` computes a read-only digest over tracked diff and untracked file content, with per-path fingerprints so a same-path edit after review is visible. Finisher compares the last reviewed snapshot with the pre-commit snapshot and labels its own closeout files or any other unreviewed changes explicitly. Planner guidance no longer assigns integration to Astra; Astra only schedules follow-up workers. The fingerprint is evidence, not a runtime permission or automatic acceptance gate.

After this correction, `python3 -m unittest discover -s tests -v` passed 58 tests; `harness/bin/check-handover`, `git diff --check`, and Python compilation passed. Live shift behavior remains outside this framework test.
