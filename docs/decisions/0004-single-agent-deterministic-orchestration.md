# ADR-004 — single-agent, deterministic orchestration (2026-10-14)
- Decision: one Claude-based agent proposes actions; a deterministic application-side orchestrator owns the analyze–propose–validate–execute–verify loop, iteration limits and accept/revert decisions. No multi-agent setup.
- Source: project brief of 2026-10-14; recorded here because it was previously only implicit in the target pipeline in `architecture.md`. This entry documents an existing decision and does not change scope.
- Rationale: keeps agent behavior attributable and reproducible, and keeps DSP and verification testable without network access (QR-02).
- Consequences: the Claude adapter (M3) returns structured proposals only; all audio changes go through the validator and DSP layer.
