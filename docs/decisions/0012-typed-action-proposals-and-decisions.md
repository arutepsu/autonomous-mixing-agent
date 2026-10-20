# ADR-012 — typed action proposals and single-outcome decisions (2026-10-19)
- Status: Proposed; awaiting owner review of the implementing task (Task 2A).
- Decision: extend the dependency-free domain layer of ADR-011 with `domain.action` and `domain.decision`.
  1. A `Decision` has exactly one typed outcome: `ProposeAction(action, expected_effect)` or `Abstain(reason, requested_context)`. There are no optional parallel action/abstention fields, unrestricted parameter dictionaries, numeric confidence scores or executable callbacks.
  2. Abstention reasons are the enum `AbstentionReason`: insufficient evidence, missing context, conflicting constraints, no justified action. Requested-context entries are explanations, not an interactive pause/resume mechanism.
  3. The first proposal vocabulary is `SetTrackGain(track_id, value_db)`: an absolute track gain in dB, finite, with no implied bounds or defaults.
  4. An `Action` is proposal vocabulary, not permission to execute. Construction checks shape only. Capabilities, producer protections, parameter bounds, magnitude limits and current-state checks belong to later application enforcement (ADR-004, FR-07).
  5. A proposal must reference at least one observation and must match the decision's project and expected revision. `validate_decision_references` checks structural references (snapshot project/revision, context identity/version, context tracks, referenced observations and their scope tracks, action target). It does not check source-audio provenance (`validate_observation_sources`) or whether evidence justifies the action.
- Source: owner's Task 2A instruction of 2026-10-19, which splits the original plan's Task 2 into smaller tasks.
- Rationale: one typed outcome keeps controller output unambiguous and machine-checkable for FR-06/FR-07, and makes abstention a first-class recorded result rather than an absent action. Keeping enforcement out of the records preserves the ADR-004 split between proposals (agent) and validation and execution (application code).
- Consequences:
  - Groundwork only for FR-06, FR-07, FR-11 and FR-12; none of these is met. FR-08 is not met, and D5 (action types and bounds) remains open: `SetTrackGain` is not a decision that gain is the correction action for any problem family.
  - Problem candidates (FR-05, D11), validation criteria and results, run records, budgets, execution and restoration are not defined.
  - Gain is modelled per track only; bus, group or plugin targets would need new operation types.
