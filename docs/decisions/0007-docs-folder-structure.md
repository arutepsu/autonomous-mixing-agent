# ADR-007 — documentation folder structure and one file per ADR (2026-10-15)
- Decision: group `docs/` by topic into `decisions/`, `architecture/`, `research/` and `project/`, and store each ADR as its own file `decisions/NNNN-short-title.md`, indexed in `decisions/README.md`. Moves: `architecture.md` → `architecture/overview.md`; `project-scope.md`, `methodology.md`, `dataset-plan.md`, `research-log.md` → `research/`; `requirements.md`, `roadmap.md`, `documentation-policy.md` → `project/`; `decisions.md` split into ADR-001 to ADR-006.
- Source: owner request of 2026-10-15.
- Rationale: one file per ADR makes the append-only rule (ADR-003) enforceable per decision and keeps diffs attributable. Topic folders separate thesis-science documents (`research/`) from engineering (`architecture/`) and process documents (`project/`), and leave room for per-component architecture pages from M1 onward.
- Consequences:
  - ADR-001 to ADR-006 were copied verbatim from `decisions.md`; only their heading level changed from `##` to `#`. File paths mentioned inside them, and inside earlier `research-log.md` entries, refer to the flat layout that was current when they were written.
  - An accepted ADR file is not edited after acceptance; changes are made through a new ADR that supersedes it, recorded in the index.
  - Folders are created only when they have content (ADR-006). `research/literature/` is planned for M1 literature notes and does not exist yet.
  - The README documentation map, `CLAUDE.md` and links in the living documents point to the new paths. Git history is preserved via `git mv`; `decisions.md` history remains in Git under its old path.
