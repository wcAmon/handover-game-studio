# Framework cloud backup and restore

This repository is the reusable handover framework. `examples/swarm-agent/` preserves the approved design and concept art as an exportable example; it does not contain the playable game's source or development history. The separately developed game is in the private [wcAmon/swarm-agent-work](https://github.com/wcAmon/swarm-agent-work) repository, branch `codex/swarm-agent`. Its backup checkpoint is `12090dbe532bca2291d2cc43b39750979e0c7bad` and its supervisor was paused after shift 47. Do not copy it into this repository root or start a shift from the design-only example.

The cloud backup branch is `claude/inspiring-feynman-46c62a`. Select this branch explicitly when restoring so a future default-branch change does not select an older line of work:

```sh
git clone --branch claude/inspiring-feynman-46c62a --single-branch https://github.com/wcAmon/handover-game-studio.git
cd handover-game-studio
git status --short --branch
```

The pre-backup framework checkpoint was `03e3c1c792b8c4636df4917a29f9deb6e54f91cf`. Later backup commits are on the same branch. Read `AGENTS.md`, `handover.md`, `docs/DESIGN.md`, and `docs/WORKFLOW.md` before changing the framework. The seven dated files in `docs/reviews/` preserve the analysis and source-backed metrics that were untracked at backup time. One unnecessary absolute home path was changed to a workspace-relative reference, and internal agent session IDs were removed from the public usage-attribution JSON. Its complete source is retained in the private game backup.

The intentionally excluded files are generated dependencies and builds (`node_modules/`, `dist/`), local machine configuration (`harness/config.local.sh`), `.studio/` runtime state, lock/PID files, Python cache, and `.DS_Store`. Never restore `.studio` runtime PIDs or locks from another machine. No framework LFS objects are required. The game repository carries its own portable paused-state snapshot and sanitized logs.
