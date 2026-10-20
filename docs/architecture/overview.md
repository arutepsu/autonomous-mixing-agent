# Architecture

## Confirmed decisions
- Offline Python processing of synchronized WAV stems; modular monolith with a CLI; no DAW plugin in M0 ([ADR-001](../decisions/0001-offline-python-workflow.md)).
- Deterministic audio analysis and DSP; Claude proposes structured actions but never performs measurements or audio processing ([ADR-001](../decisions/0001-offline-python-workflow.md)).
- Single agent with deterministic orchestration: application code controls the loop, validates proposals, executes DSP and verifies results ([ADR-004](../decisions/0004-single-agent-deterministic-orchestration.md)).
- uv-managed environment, Python 3.11 ([ADR-002](../decisions/0002-uv-dependency-management.md)).
- Track-role-agnostic design: stems carry declared roles; components must not assume specific instruments such as kick/bass. Problem-specific components are added only in their roadmap phase; analysis parameters and thresholds must be configurable and documented ([ADR-006](../decisions/0006-research-first-development-policy.md)).

## Target pipeline (planned)
Audio I/O -> deterministic features -> detectors -> structured problem candidates -> Claude proposal (`decision_agent`) -> action validator -> DSP execution -> verification -> accept/revert -> experiment report.

Hidden-reference boundary ([ADR-010](../decisions/0010-hidden-reference-boundary.md), requirements SR-10): everything up to accept/revert is runtime and never reads the original reference audio or defect-injection ground truth. Run records hold runtime inputs and the action history. Research evaluation joins them with the separately stored hidden evaluation data only after execution.

## Implemented (M0)
M0 implements only Audio I/O -> features -> descriptive JSON report. Do not claim masking detection from overlap measures alone.

| Module | Responsibility |
| --- | --- |
| `autonomous_mixing.audio.io` | Load WAV stems as float64 `(frames, channels)`; reject non-WAV, unreadable, too-short (< 2048 frames), > 2-channel and non-finite input; require equal sample rate and frame count for a pair. |
| `autonomous_mixing.audio.features` | Mono fold-down, RMS/peak dBFS, STFT magnitudes, band-power and temporal-coactivity proxies. |
| `autonomous_mixing.audio.analysis` | `analyze_pair`: combines the above into the `m0.1` report dict, including input SHA-256 hashes. |
| `autonomous_mixing.cli` | `autonomous-mixing analyze`: writes the JSON report; validation errors exit with code 2 and a one-line message. |
| `scripts/generate_test_audio.py` | Deterministic synthetic kick/bass stems, formerly used for manual smoke runs (not perceptual ground truth). No test depends on it; under review per ADR-006. |

Analysis parameters (STFT 2048/512, 30–200 Hz band, 10 % coactivity threshold) are fixed in code. `configs/analysis.yaml` documents them as a proposed manifest but is **not read** by the code yet.

**Known deviations from ADR-006 (M0):** the two inputs are named `kick`/`bass` in the CLI, `analyze_pair` and the report keys, and the parameters above are hardcoded. Retained unchanged until reviewed; do not extend this pattern.

## Domain foundation (implemented records; not integrated)
Proposed in [ADR-011](../decisions/0011-domain-foundation-boundary.md), [ADR-012](../decisions/0012-typed-action-proposals-and-decisions.md), [ADR-013](../decisions/0013-validation-criteria-and-result-records.md), [ADR-014](../decisions/0014-run-lifecycle-and-budget-records.md) and [ADR-015](../decisions/0015-correction-attempt-and-artifact-checkpoint-records.md). `autonomous_mixing.domain` holds immutable, standard-library-only records with construction-time invariants. Evidence: `tests/unit/test_domain_foundation.py`, which also enforces the import boundary, `tests/unit/test_action_decision.py`, `tests/unit/test_validation_records.py`, `tests/unit/test_run_records.py` and `tests/unit/test_execution_records.py`. M0 does not use these records yet; no requirement is met by them alone.

| Module | Responsibility |
| --- | --- |
| `autonomous_mixing.domain.values` | Opaque IDs (`ProjectId`, `TrackId`, `ArtifactId`, `ObservationId`, `ContextId`, `ActionId`, `DecisionId`, `CriteriaId`, `ConditionId`, `ValidationResultId`, `RunId`, `AttemptId`, `ExecutionId`, `CheckpointId`, `Revision`), `VersionRef`, finite-number, count and UTC-timestamp validation. |
| `autonomous_mixing.domain.project` | `TimeRange`, `FrequencyRange`, `Track`, `ProjectSnapshot`, `AnalysisScope`, `ArtifactKind`, `AudioArtifact` (metadata only; `revision` is the production revision, never retagged; derived end time and Nyquist must be finite). |
| `autonomous_mixing.domain.context` | `AssertionSource`, `TrackRole`, `ContextPreference`, `MusicalContext`; roles are explicit, unknown is absence. |
| `autonomous_mixing.domain.observation` | `MeasuredScalar`, `Unavailable`, `AnalysisSpec`, `RenderSpec`, `Observation`, `validate_observation_sources` (sources must be members of an explicit checkpoint matching the snapshot, with identical recorded metadata; production revisions may differ). |
| `autonomous_mixing.domain.action` | `SetTrackGain` (absolute track gain in dB, no implied bounds), `Action`; proposal vocabulary only, not permission to execute. |
| `autonomous_mixing.domain.decision` | `ControllerIdentity`, `ProposeAction`, `AbstentionReason`, `Abstain`, `Decision` (exactly one outcome), `validate_decision_references` (structural references only). |
| `autonomous_mixing.domain.validation` | `MetricSelector`, `TargetCondition`, `ImprovementCondition`, `AbsoluteGuard`, `DeltaGuard`, `ValidationCriteria`, `CheckResult`, `ValidationResult` and their enums; `validate_validation_references` (record consistency only). No evaluator, metric formulas or thresholds. |
| `autonomous_mixing.domain.run` | `RunState`, `RunOutcome`, `FinalProjectState`, `BudgetLimits`, `BudgetUsage` (overruns representable), `RunConfiguration` (embedded fixed inputs; `validate_against` checks references, scope containment and render Nyquist limits), `Run` (record only, no transition methods), `AttemptDisposition`, `CorrectionAttempt` (links decision, execution, validation and rollback evidence), `validate_attempt_references`. |
| `autonomous_mixing.domain.execution` | `ArtifactCheckpoint` (artifact membership of one candidate or accepted state; existence is not acceptance), `ExecutionStatus`, `ExecutionIssue`, `ExecutionReceipt` (newly produced candidate artifacts plus explicit superseded IDs), `validate_receipt_against_checkpoint`, `derive_candidate_checkpoint` (retained artifacts unchanged, then candidates; does not accept), `RollbackStatus`, `RollbackReceipt`, `validate_rollback_references`. Rollback restores accepted artifact references, not an inverse transformation; matching IDs are not proof of exact audio restoration. |

Not yet modelled: problem candidates and uncertainty (FR-05, D11), constraint/preference types (D6), action types and bounds beyond the `SetTrackGain` proposal shape (D5), track kinds/routing/controls, enforcement of protections and bounds, verdict computation and evidence compatibility (evaluator), budget enforcement, lifecycle transitions, dependency invalidation of derived artifacts, artifact I/O, hashing and integrity verification, candidate cleanup, run events and persistence.

## Application contracts (implemented contracts; no services)
Proposed in [ADR-016](../decisions/0016-application-observation-and-decision-contracts.md). `autonomous_mixing.application` depends only on the standard library and the domain layer; the domain never imports it. Evidence: `tests/unit/test_application_contracts.py`, which also enforces both import boundaries. Nothing in M0 uses these contracts yet, and no requirement is met by them alone.

| Module | Responsibility |
| --- | --- |
| `autonomous_mixing.application.results` | `Success[T]`, `PortFailureCode`, `PortFailure` (code, message, advisory `retryable`), `PortResult = Success[T] \| PortFailure`. |
| `autonomous_mixing.application.contracts` | `AnalysisRequest`/`AnalysisResponse` and `DecisionRequest`/`DecisionResponse`; sources are supplied as an `ArtifactCheckpoint` matching the snapshot. `validate_analysis_response` (provenance, spec, metrics, scope containment, completeness, no duplicate metric/scope) and `validate_decision_response` (decision references, controller identity). |
| `autonomous_mixing.application.ports` | `AudioAnalyzer.analyze` and `DecisionController.decide` Protocols returning `PortResult`. |

Not yet defined: analyzers, controllers and other adapters, orchestration, retries, budget enforcement, persistence, CLI integration, and the deferred controller inputs (problem candidates, action capabilities and permitted actions, attempt history, raw provider responses).

## Open questions
- How should the M0 two-stem interface generalize to role-declared stems (e.g. via the `track_roles` manifest field in [`dataset-plan.md`](../research/dataset-plan.md)), and which report-schema version change does that imply?
- Should `scripts/generate_test_audio.py` be removed or retained (and if retained, for which documented purpose)? Requires owner approval.
- Domain records (ADR-011): how will units be checked against a future metric catalog? Should artifact time coverage allow a tolerance (tied to D3)? Is any zero-offset timezone acceptable as UTC, as currently implemented?
