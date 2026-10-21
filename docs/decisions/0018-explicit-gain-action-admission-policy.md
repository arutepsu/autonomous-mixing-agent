# ADR-018 — explicit gain-action admission policy (2026-10-20)
- Status: Proposed; awaiting owner review of the implementing task (Task 3B).
- Decision: add `autonomous_mixing.application.admission`, a deterministic application check that admits or rejects a decision's proposed action against explicit configuration and producer protections.
  1. Configuration: `TrackGainPermission(track_id, minimum_db, maximum_db)` gives an inclusive absolute gain range per track; bounds are finite numbers (no bool or strings) with `minimum_db <= maximum_db`; equal bounds permit one exact setting. `ActionAdmissionPolicy(reference: VersionRef, project_id, gain_permissions)` holds at most one permission per track; an empty tuple denies every gain action. No defaults or scientific limits are implied, and permission is never inferred from track names, roles, observation scopes or the existence of a track.
  2. `admit_action(ActionAdmissionRequest(decision_request, decision, policy)) -> AdmittedAction | RejectedAction` checks in a fixed order, and the first failure wins:
     1. decision references and controller via `validate_decision_response`; only its `ValueError` becomes `INVALID_REFERENCES`, and other exceptions propagate;
     2. policy project equals the snapshot project (`POLICY_PROJECT_MISMATCH`);
     3. a ProposeAction outcome (`NOT_AN_ACTION`; an abstention is valid behavior with nothing to admit);
     4. target not in the context's protected tracks (`PROTECTED_TRACK`);
     5. an explicit permission for the target (`NO_GAIN_PERMISSION`);
     6. `minimum_db <= value_db <= maximum_db` (`OUT_OF_BOUNDS`).
     The requested value is never clamped or rounded. An admitted result carries the original `Action` object and the policy reference.
  3. The request records check field types only, so reference mismatches surface as typed rejections rather than construction errors. (Clarified 2026-10-21 by [ADR-019](0019-fixed-input-gain-and-composite-project-state.md): the decision request now carries a composite state; the policy project is compared with `state.snapshot`. Decisions, codes and order are unchanged.)
- Source: owner's Task 3B instruction of 2026-10-20.
- Rationale: FR-07 requires that non-permitted, out-of-bounds or hard-constraint-violating proposals are rejected with a recorded reason and never executed; FR-11 requires hard producer constraints to be enforced; OP-01 requires that only validated corrections are executed. An explicit, versioned policy with typed rejection codes and a fixed check order makes these decisions deterministic, testable offline (QR-02) and recordable (FR-12).
- Consequences:
  - Partial enforcement groundwork only; FR-07, FR-11 and OP-01 are not met. An `AdmittedAction` is a checked proposal, not an execution receipt, permission token or security boundary, and no execution service exists yet.
  - The expected revision is checked against the supplied snapshot only; that does not prove the external state is still current. A future executor must recheck immediately before mutation.
  - Absolute gain is compared with configured absolute bounds only; its execution semantics relative to audio remain unresolved. Permissions describe configured authorization, not executor support.
  - Deferred, each needing its own contract: per-edit gain deltas and cumulative movement limits, current-gain assumptions, budget enforcement, runtime adapter capability checks, musical appropriateness, problem candidates and metric thresholds, rendering or file access, and new operation types (D5). Constraint and preference types beyond track protection remain open (D6).
