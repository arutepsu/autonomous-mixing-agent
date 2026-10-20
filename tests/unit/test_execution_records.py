"""Focused tests for artifact checkpoints, execution/rollback receipts and correction attempts (Task 2D).

All artifacts are metadata fixtures (no files are read or written); values are structural examples only.
"""

import dataclasses
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from autonomous_mixing.domain import (
    Abstain,
    AbstentionReason,
    Action,
    ActionId,
    AnalysisScope,
    AnalysisSpec,
    ArtifactCheckpoint,
    ArtifactId,
    ArtifactKind,
    AssessmentMode,
    AttemptDisposition,
    AttemptId,
    AudioArtifact,
    BudgetLimits,
    BudgetUsage,
    CheckpointId,
    CheckResult,
    CheckStatus,
    ComparisonOperator,
    ConditionId,
    ContextId,
    ControllerIdentity,
    CorrectionAttempt,
    CriteriaId,
    Decision,
    DecisionId,
    ExecutionId,
    ExecutionIssue,
    ExecutionReceipt,
    ExecutionStatus,
    ImprovementCondition,
    ImprovementDirection,
    MeasuredScalar,
    MetricSelector,
    MusicalContext,
    Observation,
    ObservationId,
    ProjectId,
    ProjectSnapshot,
    ProposeAction,
    RenderSpec,
    Revision,
    RollbackReceipt,
    RollbackStatus,
    Run,
    RunConfiguration,
    RunId,
    RunState,
    SetTrackGain,
    TargetCondition,
    TargetStatus,
    TimeRange,
    Track,
    TrackId,
    ValidationCriteria,
    ValidationResult,
    ValidationResultId,
    ValidationVerdict,
    VersionRef,
    derive_candidate_checkpoint,
    validate_attempt_references,
    validate_observation_sources,
    validate_rollback_references,
    validate_validation_references,
)

UTC_NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
HASH = "b" * 64
_D = object()
ISSUE = ExecutionIssue("render_error", "renderer reported an error")
CR, NS, FL, UN = (
    ExecutionStatus.CANDIDATE_READY,
    ExecutionStatus.NOT_STARTED,
    ExecutionStatus.FAILED,
    ExecutionStatus.UNCERTAIN,
)
D = AttemptDisposition
METRIC = VersionRef("metric-a", "1")


def _artifact(aid, tracks=("t1",), *, revision="r1", project="p1", kind=ArtifactKind.STEM) -> AudioArtifact:
    return AudioArtifact(
        artifact_id=ArtifactId(aid),
        project_id=ProjectId(project),
        revision=Revision(revision),
        source_track_ids=tuple(TrackId(t) for t in tracks),
        kind=kind,
        location=f"outputs/{aid}.wav",
        timeline_start_seconds=0.0,
        sample_rate_hz=48000,
        channel_count=2,
        frame_count=48000 * 60,
        content_hash=HASH,
        render_spec=VersionRef("render", "1"),
    )


def _checkpoint_artifacts(revision="r1", project="p1") -> tuple[AudioArtifact, ...]:
    return (
        _artifact("a-t1", ("t1",), revision=revision, project=project),
        _artifact("a-t2", ("t2",), revision=revision, project=project),
        _artifact("a-mix", ("t1", "t2"), revision=revision, project=project, kind=ArtifactKind.MIX),
    )


def _checkpoint(revision="r1", artifacts=_D, *, cid="cp1", project="p1") -> ArtifactCheckpoint:
    if artifacts is _D:
        artifacts = _checkpoint_artifacts(revision, project)
    return ArtifactCheckpoint(CheckpointId(cid), ProjectId(project), Revision(revision), artifacts)


def _receipt(
    status, revision=_D, artifacts=_D, issue=_D, *, superseded=_D, before="r1", action="x1", project="p1", eid="e1"
):
    ready = status is CR
    if superseded is _D:
        # The candidates explicitly replace the edited stem and the mix derived from it.
        superseded = (ArtifactId("a-t2"), ArtifactId("a-mix")) if ready else ()
    if revision is _D:
        revision = Revision("r2") if ready else None
    if artifacts is _D:
        # Only the edited stem and the mix are newly produced; the unchanged t1 stem stays in the checkpoint.
        artifacts = (
            (
                _artifact("c-t2", ("t2",), revision="r2", project=project),
                _artifact("c-mix", ("t1", "t2"), revision="r2", project=project, kind=ArtifactKind.MIX),
            )
            if ready
            else ()
        )
    if issue is _D:
        issue = ISSUE if status in (FL, UN) else None
    return ExecutionReceipt(
        ExecutionId(eid),
        ActionId(action),
        ProjectId(project),
        Revision(before),
        status,
        revision,
        artifacts,
        superseded,
        issue,
    )


def _rollback(status=RollbackStatus.VERIFIED, restored=_D, *, checkpoint="cp1", execution="e1") -> RollbackReceipt:
    if restored is _D:
        restored = tuple(ArtifactId(a) for a in ("a-t1", "a-t2", "a-mix")) if status is RollbackStatus.VERIFIED else ()
    return RollbackReceipt(ExecutionId(execution), CheckpointId(checkpoint), status, restored, "restoration checked")


def _criteria(version="1") -> ValidationCriteria:
    selector = MetricSelector(METRIC, AnalysisScope((TrackId("t1"), TrackId("t2")), TimeRange(0.0, 60.0)))
    return ValidationCriteria(
        CriteriaId("crit"),
        version,
        (TargetCondition(ConditionId("target"), selector, ComparisonOperator.LE, MeasuredScalar(-6.0, "unit")),),
        (
            ImprovementCondition(
                ConditionId("improve"), selector, ImprovementDirection.LOWER, MeasuredScalar(1, "unit")
            ),
        ),
        (),
    )


def _validation(verdict=ValidationVerdict.ACCEPTED, version="1") -> ValidationResult:
    def check(cid):
        return CheckResult(ConditionId(cid), CheckStatus.PASS, "passed", (ObservationId("o-after"),))

    return ValidationResult(
        ValidationResultId("v1"),
        CriteriaId("crit"),
        version,
        AssessmentMode.ATTEMPT,
        (check("target"), check("improve")),
        verdict,
        TargetStatus.SATISFIED,
    )


def _initial_validation() -> ValidationResult:
    # A consistent INITIAL assessment: target met before any edit; improvement is outside this mode.
    return ValidationResult(
        ValidationResultId("v0"),
        CriteriaId("crit"),
        "1",
        AssessmentMode.INITIAL,
        (
            CheckResult(ConditionId("target"), CheckStatus.PASS, "passed", (ObservationId("o-before"),)),
            CheckResult(ConditionId("improve"), CheckStatus.NOT_APPLICABLE, "not assessed initially", ()),
        ),
        ValidationVerdict.ACCEPTED,
        TargetStatus.SATISFIED,
    )


def _attempt(disposition, execution=None, validation=None, rollback=None, checkpoint=_D, **ids) -> CorrectionAttempt:
    return CorrectionAttempt(
        attempt_id=AttemptId(ids.get("attempt", "att1")),
        run_id=RunId(ids.get("run", "run-1")),
        decision_id=DecisionId(ids.get("decision", "d1")),
        action_id=ActionId(ids.get("action", "x1")),
        before_checkpoint=_checkpoint() if checkpoint is _D else checkpoint,
        execution=execution,
        validation=validation,
        rollback=rollback,
        disposition=disposition,
    )


def _accepted(**kwargs) -> CorrectionAttempt:
    return _attempt(D.ACCEPTED, _receipt(CR), _validation(), **kwargs)


CONTEXT = MusicalContext(ContextId("c1"), "1", (), (), frozenset())
CONTROLLER = ControllerIdentity("deterministic-baseline", "0.1")


def _run(project="p1", run_id="run-1", context=CONTEXT, controller=CONTROLLER, criteria_version="1") -> Run:
    configuration = RunConfiguration(
        scope=AnalysisScope((TrackId("t1"), TrackId("t2"), TrackId("t3")), TimeRange(0.0, 60.0)),
        analysis_spec=AnalysisSpec(VersionRef("spec", "1"), (METRIC,)),
        render_spec=RenderSpec(VersionRef("render", "1"), 48000, 2),
        context=context,
        criteria=_criteria(criteria_version),
        controller=controller,
        budget_limits=BudgetLimits(4, 2, 6, 1, 300.0),
    )
    usage = BudgetUsage(1, 1, 2, 0, 12.5)
    return Run(
        RunId(run_id),
        ProjectId(project),
        configuration,
        Revision("r1"),
        UTC_NOW,
        RunState.VALIDATING,
        usage,
        None,
        None,
        None,
    )


def _decision(revision="r1", *, project="p1", action="x1", decision="d1", context=("c1", "1"), controller=CONTROLLER):
    action_record = Action(ActionId(action), ProjectId(project), Revision(revision), SetTrackGain(TrackId("t2"), -3.0))
    return Decision(
        DecisionId(decision),
        ProjectId(project),
        Revision(revision),
        ContextId(context[0]),
        context[1],
        (ObservationId("o1"),),
        "structured rationale",
        controller,
        ProposeAction(action_record, "lower track t2"),
    )


# --- identifiers -----------------------------------------------------------------


@pytest.mark.parametrize("cls", [AttemptId, ExecutionId, CheckpointId])
@pytest.mark.parametrize("raw", ["", " ", 1, None])
def test_new_identifiers_reject_blank_and_non_string(cls, raw):
    with pytest.raises(ValueError):
        cls(raw)


def test_new_identifiers_are_distinct_kinds():
    assert AttemptId("x") != ExecutionId("x")
    assert ExecutionId("x") != CheckpointId("x")
    assert CheckpointId("x") != ArtifactId("x")


@pytest.mark.parametrize(
    "enum, names",
    [
        (ExecutionStatus, {"NOT_STARTED", "FAILED", "CANDIDATE_READY", "UNCERTAIN"}),
        (RollbackStatus, {"VERIFIED", "FAILED", "UNCERTAIN"}),
        (AttemptDisposition, {"PENDING", "ACCEPTED", "ROLLED_BACK", "FAILED", "UNRESOLVED"}),
    ],
)
def test_enums_have_exactly_the_specified_members(enum, names):
    assert {member.name for member in enum} == names


# --- checkpoints -----------------------------------------------------------------


def test_checkpoint_accepts_stems_groups_and_mix_without_full_track_coverage():
    artifacts = (
        _artifact("a-t1"),
        _artifact("a-group", ("t1", "t2"), kind=ArtifactKind.GROUP),
        _artifact("a-mix", ("t1", "t2"), kind=ArtifactKind.MIX),
    )
    checkpoint = _checkpoint(artifacts=artifacts)
    assert {a.kind for a in checkpoint.artifacts} == set(ArtifactKind)


@pytest.mark.parametrize(
    "artifacts",
    [
        (),
        list(_checkpoint_artifacts()),
        (_artifact("a-t1"), _artifact("a-t1", ("t2",))),
        (_artifact("a-t1"), _artifact("a-t2", project="p2")),
        ("a-t1",),
    ],
)
def test_checkpoint_rejects_empty_mutable_duplicate_and_mislinked_artifacts(artifacts):
    with pytest.raises(ValueError):
        _checkpoint(artifacts=artifacts)


def test_checkpoint_rejects_untyped_identity():
    with pytest.raises(ValueError):
        ArtifactCheckpoint("cp1", ProjectId("p1"), Revision("r1"), _checkpoint_artifacts())
    with pytest.raises(ValueError):
        ArtifactCheckpoint(CheckpointId("cp1"), ProjectId("p1"), "r1", _checkpoint_artifacts())


# --- execution receipts ----------------------------------------------------------


@pytest.mark.parametrize("status", list(ExecutionStatus))
def test_every_execution_status_has_a_valid_shape(status):
    receipt = _receipt(status)
    assert receipt.status is status


def test_not_started_may_record_an_issue():
    assert _receipt(NS, issue=ISSUE).issue == ISSUE


def test_candidate_artifacts_cover_only_newly_produced_outputs():
    receipt = _receipt(CR)
    checkpoint = _checkpoint()
    produced = {a.artifact_id for a in receipt.candidate_artifacts}
    assert ArtifactId("a-t1") in {a.artifact_id for a in checkpoint.artifacts}
    assert not any(
        TrackId("t1") == a.source_track_ids[0] and a.kind is ArtifactKind.STEM for a in receipt.candidate_artifacts
    )
    assert produced == {ArtifactId("c-t2"), ArtifactId("c-mix")}


@pytest.mark.parametrize(
    "status, revision, artifacts, issue",
    [
        (CR, None, _D, _D),
        (CR, Revision("r1"), (_artifact("c-t2", revision="r1"),), _D),
        (CR, _D, (), _D),
        (CR, _D, _D, ISSUE),
        (NS, Revision("r2"), _D, _D),
        (NS, None, (_artifact("c-t2", revision="r2"),), _D),
        (FL, _D, _D, None),
        (FL, Revision("r2"), _D, _D),
        (FL, None, (_artifact("c-t2", revision="r2"),), _D),
        (UN, _D, _D, None),
        (UN, Revision("r2"), _D, _D),
        (UN, None, (_artifact("c-t2", revision="r2"),), _D),
    ],
)
def test_execution_receipt_rejects_contradictory_shapes(status, revision, artifacts, issue):
    with pytest.raises(ValueError):
        _receipt(status, revision, artifacts, issue)


@pytest.mark.parametrize(
    "artifacts",
    [
        (_artifact("c-t2", revision="r3"),),
        (_artifact("c-t2", revision="r2", project="p2"),),
        (_artifact("c-t2", revision="r2"), _artifact("c-t2", ("t1",), revision="r2")),
        [_artifact("c-t2", revision="r2")],
    ],
)
def test_candidate_artifacts_must_be_unique_and_match_project_and_candidate_revision(artifacts):
    with pytest.raises(ValueError):
        _receipt(CR, Revision("r2"), artifacts)


@pytest.mark.parametrize("code, message", [("", "m"), ("c", " "), (None, "m")])
def test_execution_issue_requires_code_and_message(code, message):
    with pytest.raises(ValueError):
        ExecutionIssue(code, message)


def test_execution_receipt_rejects_untyped_fields():
    with pytest.raises(ValueError):
        _receipt("CANDIDATE_READY")
    with pytest.raises(ValueError):
        _receipt(FL, issue="render failed")


# --- rollback receipts -----------------------------------------------------------


def test_verified_rollback_restores_exactly_the_checkpoint_artifacts():
    validate_rollback_references(_rollback(), _checkpoint())


@pytest.mark.parametrize(
    "status, restored",
    [
        (RollbackStatus.VERIFIED, ()),
        (RollbackStatus.FAILED, (ArtifactId("a-t1"),)),
        (RollbackStatus.UNCERTAIN, (ArtifactId("a-t1"),)),
        (RollbackStatus.VERIFIED, (ArtifactId("a-t1"), ArtifactId("a-t1"))),
        (RollbackStatus.VERIFIED, [ArtifactId("a-t1")]),
        ("VERIFIED", (ArtifactId("a-t1"),)),
    ],
)
def test_rollback_receipt_rejects_contradictory_shapes(status, restored):
    with pytest.raises(ValueError):
        _rollback(status, restored)


def test_rollback_receipt_requires_explanation():
    with pytest.raises(ValueError):
        RollbackReceipt(ExecutionId("e1"), CheckpointId("cp1"), RollbackStatus.FAILED, (), " ")


@pytest.mark.parametrize(
    "receipt, match",
    [
        (_rollback(restored=(ArtifactId("a-t1"), ArtifactId("a-t2"))), "a-mix"),
        (_rollback(restored=(ArtifactId("a-t1"), ArtifactId("a-t2"), ArtifactId("a-mix"), ArtifactId("c-t2"))), "c-t2"),
        (_rollback(checkpoint="cp0"), "checkpoint"),
    ],
)
def test_rollback_references_reject_missing_additional_and_mismatched_checkpoint(receipt, match):
    with pytest.raises(ValueError, match=match):
        validate_rollback_references(receipt, _checkpoint())


@pytest.mark.parametrize("status", [RollbackStatus.FAILED, RollbackStatus.UNCERTAIN])
def test_unsuccessful_rollback_references_need_only_checkpoint_identity(status):
    validate_rollback_references(_rollback(status), _checkpoint())


# --- correction attempts ---------------------------------------------------------


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.PENDING),
        lambda: _attempt(D.PENDING, _receipt(CR)),
        lambda: _attempt(D.PENDING, _receipt(CR), _validation(ValidationVerdict.REJECTED)),
        lambda: _accepted(),
        lambda: _attempt(D.ROLLED_BACK, _receipt(CR), _validation(ValidationVerdict.REJECTED), _rollback()),
        lambda: _attempt(D.ROLLED_BACK, _receipt(UN), None, _rollback()),
        lambda: _attempt(D.FAILED, _receipt(NS)),
        lambda: _attempt(D.FAILED, _receipt(FL)),
        lambda: _attempt(D.UNRESOLVED, _receipt(UN)),
        lambda: _attempt(
            D.UNRESOLVED, _receipt(CR), _validation(ValidationVerdict.REJECTED), _rollback(RollbackStatus.FAILED)
        ),
        lambda: _attempt(D.UNRESOLVED, _receipt(CR), None, _rollback(RollbackStatus.UNCERTAIN)),
    ],
    ids=[
        "pending-empty",
        "pending-candidate",
        "pending-validated",
        "accepted",
        "rolled-back-after-rejection",
        "rolled-back-after-uncertain-execution",
        "failed-not-started",
        "failed-execution",
        "unresolved-execution",
        "unresolved-failed-rollback",
        "unresolved-uncertain-rollback",
    ],
)
def test_every_disposition_has_valid_evidence_shapes(build):
    assert isinstance(build().disposition, AttemptDisposition)


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.PENDING, _receipt(CR, action="x2")),
        lambda: _attempt(D.PENDING, _receipt(CR, project="p2")),
        lambda: _attempt(D.PENDING, _receipt(CR, before="r0")),
    ],
    ids=["action", "project", "before-revision"],
)
def test_attempt_rejects_receipt_disagreeing_with_attempt_or_checkpoint(build):
    with pytest.raises(ValueError):
        build()


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.PENDING, None, _validation()),
        lambda: _attempt(D.PENDING, _receipt(FL), _validation(ValidationVerdict.REJECTED)),
        lambda: _attempt(D.PENDING, _receipt(UN), _validation(ValidationVerdict.INCONCLUSIVE)),
    ],
    ids=["no-execution", "failed-execution", "uncertain-execution"],
)
def test_validation_requires_candidate_ready_execution(build):
    with pytest.raises(ValueError, match="CANDIDATE_READY"):
        build()


def test_accepted_attempt_rejects_initial_assessment_as_validation():
    with pytest.raises(ValueError, match="ATTEMPT"):
        _attempt(D.ACCEPTED, _receipt(CR), _initial_validation())


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.PENDING, _receipt(CR), _initial_validation()),
        lambda: _attempt(D.ROLLED_BACK, _receipt(CR), _initial_validation(), _rollback()),
    ],
    ids=["pending", "rolled-back"],
)
def test_other_dispositions_reject_embedded_initial_assessment(build):
    with pytest.raises(ValueError, match="ATTEMPT"):
        build()


def test_attempt_mode_assessments_remain_supported():
    attempt = _accepted()
    assert attempt.validation.mode is AssessmentMode.ATTEMPT
    validate_attempt_references(attempt, _run(), _decision())


def test_standalone_initial_assessment_remains_valid_outside_attempts():
    validate_validation_references(_initial_validation(), _criteria())


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.ACCEPTED),
        lambda: _attempt(D.ACCEPTED, _receipt(CR)),
        lambda: _attempt(D.ACCEPTED, _receipt(CR), _validation(ValidationVerdict.REJECTED)),
        lambda: _attempt(D.ACCEPTED, _receipt(CR), _validation(ValidationVerdict.INCONCLUSIVE)),
        lambda: _attempt(D.ACCEPTED, _receipt(CR), _validation(), _rollback()),
    ],
    ids=["no-execution", "no-validation", "rejected", "inconclusive", "with-rollback"],
)
def test_accepted_requires_candidate_and_accepted_validation_without_rollback(build):
    with pytest.raises(ValueError, match="ACCEPTED"):
        build()


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.ROLLED_BACK, _receipt(CR)),
        lambda: _attempt(D.ROLLED_BACK, _receipt(CR), None, _rollback(RollbackStatus.FAILED)),
        lambda: _attempt(D.ROLLED_BACK, _receipt(CR), None, _rollback(RollbackStatus.UNCERTAIN)),
    ],
    ids=["no-rollback", "failed-rollback", "uncertain-rollback"],
)
def test_rolled_back_requires_verified_rollback(build):
    with pytest.raises(ValueError, match="ROLLED_BACK"):
        build()


@pytest.mark.parametrize(
    "build, match",
    [
        (lambda: _attempt(D.PENDING, None, None, _rollback(RollbackStatus.FAILED)), "execution"),
        (lambda: _attempt(D.ROLLED_BACK, _receipt(CR), None, _rollback(execution="e9")), "execution"),
        (lambda: _attempt(D.ROLLED_BACK, _receipt(CR), None, _rollback(checkpoint="cp0")), "checkpoint"),
        (
            lambda: _attempt(D.ROLLED_BACK, _receipt(CR), None, _rollback(restored=(ArtifactId("a-t1"),))),
            "a-mix",
        ),
    ],
    ids=["without-execution", "execution-mismatch", "checkpoint-mismatch", "incomplete-restoration"],
)
def test_attempt_rejects_mismatched_rollback_references(build, match):
    with pytest.raises(ValueError, match=match):
        build()


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.FAILED),
        lambda: _attempt(D.FAILED, _receipt(UN)),
        lambda: _attempt(D.FAILED, _receipt(CR)),
        lambda: _attempt(D.FAILED, _receipt(FL), None, _rollback(RollbackStatus.FAILED)),
        lambda: _attempt(D.FAILED, _receipt(CR), None, _rollback(RollbackStatus.UNCERTAIN)),
    ],
    ids=["no-execution", "uncertain-execution", "candidate-ready", "failed-rollback", "uncertain-rollback"],
)
def test_failed_requires_known_unsuccessful_execution_without_rollback(build):
    with pytest.raises(ValueError, match="FAILED"):
        build()


@pytest.mark.parametrize(
    "build",
    [
        lambda: _attempt(D.UNRESOLVED),
        lambda: _attempt(D.UNRESOLVED, _receipt(FL)),
        lambda: _attempt(D.UNRESOLVED, _receipt(CR), _validation(ValidationVerdict.REJECTED), _rollback()),
    ],
    ids=["no-evidence", "known-failure", "verified-rollback"],
)
def test_unresolved_requires_uncertain_execution_or_unsuccessful_rollback(build):
    with pytest.raises(ValueError, match="UNRESOLVED"):
        build()


def test_attempt_rejects_untyped_fields():
    with pytest.raises(ValueError):
        _attempt("ACCEPTED", _receipt(CR), _validation())
    with pytest.raises(ValueError):
        _attempt(D.PENDING, checkpoint=_checkpoint_artifacts())
    with pytest.raises(ValueError):
        _attempt(D.PENDING, execution="e1")


def test_attempt_records_are_immutable():
    attempt = _attempt(D.ROLLED_BACK, _receipt(CR), _validation(ValidationVerdict.REJECTED), _rollback())
    assert isinstance(attempt.before_checkpoint.artifacts, tuple)
    assert isinstance(attempt.execution.candidate_artifacts, tuple)
    assert isinstance(attempt.rollback.restored_artifact_ids, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        attempt.disposition = D.ACCEPTED
    with pytest.raises(dataclasses.FrozenInstanceError):
        attempt.execution.status = ExecutionStatus.FAILED
    with pytest.raises(dataclasses.FrozenInstanceError):
        attempt.before_checkpoint.artifacts[0].content_hash = "c" * 64
    with pytest.raises(dataclasses.FrozenInstanceError):
        attempt.rollback.status = RollbackStatus.FAILED


# --- cross-record references -----------------------------------------------------


def test_attempt_references_accept_matching_run_and_decision():
    validate_attempt_references(_accepted(), _run(), _decision())


def test_later_attempt_checkpoint_may_differ_from_initial_revision():
    attempt = _attempt(D.PENDING, _receipt(CR, before="r5"), checkpoint=_checkpoint("r5", cid="cp5"))
    run = _run()
    assert run.initial_revision == Revision("r1")
    validate_attempt_references(attempt, run, _decision("r5"))


def _abstain_decision() -> Decision:
    return dataclasses.replace(_decision(), outcome=Abstain(AbstentionReason.NO_JUSTIFIED_ACTION))


@pytest.mark.parametrize(
    "attempt, run, decision, match",
    [
        (lambda: _accepted(run="run-9"), _run, _decision, "run"),
        (lambda: _accepted(decision="d9"), _run, _decision, "decision"),
        (_accepted, _run, lambda: _decision(action="x9"), "action"),
        (_accepted, _run, _abstain_decision, "ProposeAction"),
        (_accepted, lambda: _run(project="p9"), _decision, "project"),
        (_accepted, _run, lambda: _decision(project="p9"), "project"),
        (_accepted, _run, lambda: _decision("r0"), "revision"),
        (_accepted, _run, lambda: _decision(context=("c9", "1")), "context"),
        (_accepted, _run, lambda: _decision(context=("c1", "2")), "context"),
        (_accepted, _run, lambda: _decision(controller=ControllerIdentity("llm", "1")), "controller"),
        (_accepted, lambda: _run(criteria_version="2"), _decision, "criteria"),
    ],
    ids=[
        "run-id",
        "decision-id",
        "action-id",
        "abstention",
        "run-project",
        "decision-project",
        "decision-revision",
        "context-id",
        "context-version",
        "controller",
        "validation-criteria",
    ],
)
def test_attempt_references_reject_mismatches(attempt, run, decision, match):
    with pytest.raises(ValueError, match=match):
        validate_attempt_references(attempt(), run(), decision())


def test_attempt_references_reject_checkpoint_tracks_outside_run_scope():
    artifacts = (_artifact("a-t1"), _artifact("a-t4", ("t4",)))
    attempt = _attempt(D.PENDING, checkpoint=_checkpoint(artifacts=artifacts))
    with pytest.raises(ValueError, match="t4"):
        validate_attempt_references(attempt, _run(), _decision())


# --- provenance, explicit replacement and candidate membership -------------------


def test_checkpoint_membership_may_mix_production_revisions():
    artifacts = (_artifact("a-t1", revision="r1"), _artifact("c-t2", ("t2",), revision="r2"))
    checkpoint = _checkpoint("r2", artifacts)
    assert [a.revision for a in checkpoint.artifacts] == [Revision("r1"), Revision("r2")]


@pytest.mark.parametrize(
    "status, superseded",
    [
        (CR, ()),
        (CR, (ArtifactId("a-t2"), ArtifactId("a-t2"))),
        (CR, [ArtifactId("a-t2")]),
        (CR, ("a-t2",)),
        (CR, (ArtifactId("c-t2"),)),
        (NS, (ArtifactId("a-t2"),)),
        (FL, (ArtifactId("a-t2"),)),
        (UN, (ArtifactId("a-t2"),)),
    ],
    ids=[
        "ready-empty",
        "duplicate",
        "list",
        "untyped",
        "supersedes-own-candidate",
        "not-started",
        "failed",
        "uncertain",
    ],
)
def test_receipt_rejects_invalid_superseded_ids(status, superseded):
    with pytest.raises(ValueError):
        _receipt(status, superseded=superseded)


@pytest.mark.parametrize(
    "receipt, match",
    [
        (lambda: _receipt(CR, superseded=(ArtifactId("a-t2"), ArtifactId("a-gone"))), "a-gone"),
        (
            lambda: _receipt(
                CR, artifacts=(_artifact("a-t1", ("t1",), revision="r2"),), superseded=(ArtifactId("a-t2"),)
            ),
            "a-t1",
        ),
    ],
    ids=["missing-superseded", "reused-candidate-id"],
)
def test_attempt_rejects_superseded_ids_outside_checkpoint_and_reused_candidate_ids(receipt, match):
    with pytest.raises(ValueError, match=match):
        _attempt(D.PENDING, receipt())
    with pytest.raises(ValueError, match=match):
        derive_candidate_checkpoint(_checkpoint(), receipt(), CheckpointId("cp2"))


def test_derivation_replaces_superseded_artifacts_deterministically_and_preserves_provenance():
    previous = _checkpoint()
    receipt = _receipt(CR)
    derived = derive_candidate_checkpoint(previous, receipt, CheckpointId("cp2"))
    assert derived.checkpoint_id == CheckpointId("cp2")
    assert derived.project_id == previous.project_id
    assert derived.revision == receipt.candidate_revision
    assert [str(a.artifact_id) for a in derived.artifacts] == ["a-t1", "c-t2", "c-mix"]
    assert derived.artifacts[0] is previous.artifacts[0]  # retained unchanged: same identity, hash, location
    assert derived.artifacts[0].revision == Revision("r1")  # original production revision, not retagged
    assert derive_candidate_checkpoint(previous, receipt, CheckpointId("cp2")) == derived
    assert previous == _checkpoint()


@pytest.mark.parametrize("status", [NS, FL, UN])
def test_derivation_requires_candidate_ready_execution(status):
    with pytest.raises(ValueError, match="CANDIDATE_READY"):
        derive_candidate_checkpoint(_checkpoint(), _receipt(status), CheckpointId("cp2"))


@pytest.mark.parametrize(
    "receipt",
    [lambda: _receipt(CR, before="r0"), lambda: _receipt(CR, project="p2", superseded=(ArtifactId("a-t2"),))],
    ids=["before-revision", "project"],
)
def test_derivation_requires_matching_project_and_before_revision(receipt):
    with pytest.raises(ValueError):
        derive_candidate_checkpoint(_checkpoint(), receipt(), CheckpointId("cp2"))


def test_derivation_does_not_accept_the_attempt():
    attempt = _attempt(D.PENDING, _receipt(CR))
    derived = derive_candidate_checkpoint(attempt.before_checkpoint, attempt.execution, CheckpointId("cp2"))
    assert attempt.disposition is D.PENDING
    assert attempt.before_checkpoint == _checkpoint()
    assert isinstance(derived, ArtifactCheckpoint) and not hasattr(derived, "accepted")


def test_two_successive_corrections_retain_unchanged_older_artifacts():
    first = _attempt(D.ACCEPTED, _receipt(CR), _validation())
    cp2 = derive_candidate_checkpoint(first.before_checkpoint, first.execution, CheckpointId("cp2"))

    second_receipt = ExecutionReceipt(
        ExecutionId("e2"),
        ActionId("x2"),
        ProjectId("p1"),
        Revision("r2"),
        CR,
        Revision("r3"),
        (
            _artifact("c2-t2", ("t2",), revision="r3"),
            _artifact("c2-mix", ("t1", "t2"), revision="r3", kind=ArtifactKind.MIX),
        ),
        (ArtifactId("c-t2"), ArtifactId("c-mix")),
        None,
    )
    second = _attempt(
        D.ACCEPTED, second_receipt, _validation(), checkpoint=cp2, attempt="att2", action="x2", decision="d2"
    )
    validate_attempt_references(second, _run(), _decision("r2", action="x2", decision="d2"))
    cp3 = derive_candidate_checkpoint(cp2, second_receipt, CheckpointId("cp3"))

    assert cp3.revision == Revision("r3")
    assert [(str(a.artifact_id), str(a.revision)) for a in cp3.artifacts] == [
        ("a-t1", "r1"),
        ("c2-t2", "r3"),
        ("c2-mix", "r3"),
    ]
    assert cp3.artifacts[0] is first.before_checkpoint.artifacts[0]


def test_candidate_observation_uses_mixed_production_revision_membership():
    candidate = derive_candidate_checkpoint(_checkpoint(), _receipt(CR), CheckpointId("cp2"))
    snapshot = ProjectSnapshot(
        ProjectId("p1"), Revision("r2"), UTC_NOW, (Track(TrackId("t1"), "Room"), Track(TrackId("t2"), "Voice"))
    )
    observation = Observation(
        ObservationId("o-cand"),
        METRIC,
        (ArtifactId("a-t1"), ArtifactId("c-t2")),
        AnalysisScope((TrackId("t1"), TrackId("t2")), TimeRange(0.0, 60.0)),
        MeasuredScalar(-14.0, "unit"),
        VersionRef("spec", "1"),
        VersionRef("analyzer", "0.1"),
        UTC_NOW,
    )
    validate_observation_sources(observation, candidate.artifacts, candidate, snapshot)
    # A superseded artifact of the previous state is not a member of the candidate state.
    stale = dataclasses.replace(observation, artifact_ids=(ArtifactId("a-t1"), ArtifactId("a-t2")))
    with pytest.raises(ValueError, match="not a member"):
        validate_observation_sources(stale, (_artifact("a-t1"), _artifact("a-t2", ("t2",))), candidate, snapshot)


# --- dependency boundary ---------------------------------------------------------


def test_execution_and_run_modules_load_only_standard_library_and_domain_modules():
    # Complements the AST scan in test_domain_foundation.py, which covers every module in the domain package.
    script = (
        "import sys\n"
        "before = set(sys.modules)\n"
        "import autonomous_mixing.domain.execution, autonomous_mixing.domain.run\n"
        "for name in sorted(set(sys.modules) - before):\n"
        "    top = name.split('.')[0]\n"
        "    ok = top in sys.stdlib_module_names or name == 'autonomous_mixing' \\\n"
        "        or name == 'autonomous_mixing.domain' or name.startswith('autonomous_mixing.domain.')\n"
        "    if not ok: print(name)\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
    assert result.stdout == ""
