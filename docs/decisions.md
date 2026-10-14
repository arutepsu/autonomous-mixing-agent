# ADR-001 (2026-10-14)
- Offline Python WAV workflow first.
- Claude API planned for action selection, not DSP measurements.
- Self-created controlled project data, partitioned into calibration/evaluation sets.
- Modular monolith with CLI; no DAW plugin in M0.

## ADR-002 — uv dependency management (2026-10-14)
- Decision: retain existing `pyproject.toml` and move to uv-managed environments, with `.python-version` 3.11 and committed `uv.lock` when generated.
- Rationale: easy, consistent setup and reproducible dependency resolution.
- Consequences: run commands through `uv run`; do not use `uv init` over existing project.

## ADR-003 — documentation governance (2026-10-14)
- Decision: use topic-owned living docs, append-only decision/research logs, and root `CLAUDE.md` instructions.
- Rationale: limit conflicting instructions and prevent untracked overwrites by coding assistants.
- Consequences: architectural changes need new ADRs; factual progress needs tests and log entries.

## ADR-004 — single-agent, deterministic orchestration (2026-10-14)
- Decision: one Claude-based agent proposes actions; a deterministic application-side orchestrator owns the analyze–propose–validate–execute–verify loop, iteration limits and accept/revert decisions. No multi-agent setup.
- Source: project brief of 2026-10-14; recorded here because it was previously only implicit in the target pipeline in `architecture.md`. This entry documents an existing decision and does not change scope.
- Rationale: keeps agent behavior attributable and reproducible, and keeps DSP and verification testable without network access (QR-02).
- Consequences: the Claude adapter (M3) returns structured proposals only; all audio changes go through the validator and DSP layer.
