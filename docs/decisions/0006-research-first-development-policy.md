# ADR-006 — research-first development policy (2026-10-15)
- Decision: development serves the research system, not demonstrations. Specifically:
  1. No demo-driven work: no artificial end-to-end examples, generated example music, or temporary functionality added to make the system appear operational.
  2. Every feature traces to a documented requirement (`requirements.md`) or experiment; no undocumented temporary features.
  3. Architecture is track-role-agnostic: stems carry declared roles (cf. `track_roles` in `dataset-plan.md`); no component is designed specifically for kick/bass inputs. Kick/bass remains the first *problem family* in `project-scope.md`, i.e. a use case, not an architectural assumption.
  4. Problem-specific functionality (e.g. masking detection) is implemented only in its scheduled roadmap milestone (`roadmap.md`).
  5. No hardcoded musical assumptions or arbitrary detection thresholds: every analysis parameter or threshold is configurable and documented with its source (literature or calibration split); unjustified values are listed as assumptions requiring validation in `methodology.md`.
  6. Synthetic numerical signals are permitted only for focused, reproducible unit tests of signal-processing code. Generated audio is never a scientific evaluation dataset.
- Source: owner's development-policy correction of 2026-10-15.
- Rationale: scientific validity, traceability and maintainability over the appearance of progress (cf. ADR-003, `methodology.md`).
- Consequences:
  - Validation of changes uses package/import checks, CLI registration and unit tests, not demo runs.
  - Existing deviations are kept until reviewed rather than silently removed: the M0 interface names its two inputs `kick`/`bass` (CLI, `analyze_pair`, report keys) and fixes the 30–200 Hz band and 10 % activity threshold in code; `scripts/generate_test_audio.py` generates synthetic kick/bass stems that no test depends on. Their generalization or removal requires review and owner approval (see `architecture.md` open questions).
