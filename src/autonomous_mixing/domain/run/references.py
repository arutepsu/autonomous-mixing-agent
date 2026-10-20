"""Cross-record reference check of a correction attempt against its run and decision."""

from autonomous_mixing.domain.decision import Decision, ProposeAction
from autonomous_mixing.domain.run.attempt import CorrectionAttempt
from autonomous_mixing.domain.run.run import Run
from autonomous_mixing.domain.validation import validate_validation_references


def validate_attempt_references(attempt: CorrectionAttempt, run: Run, decision: Decision) -> None:
    """Check an attempt's references against its run and decision.

    Does not check execution permissions, evidence sufficiency, file integrity or lifecycle
    transitions. The checkpoint may follow earlier accepted attempts, so its revision need not
    equal ``run.initial_revision``.
    """
    if attempt.run_id != run.run_id:
        raise ValueError(f"attempt belongs to run {attempt.run_id}, not {run.run_id}")
    if attempt.decision_id != decision.decision_id:
        raise ValueError(f"attempt refers to decision {attempt.decision_id}, not {decision.decision_id}")
    if not isinstance(decision.outcome, ProposeAction):
        raise ValueError("attempt requires a decision with a ProposeAction outcome")
    if decision.outcome.action.action_id != attempt.action_id:
        raise ValueError(
            f"decision action {decision.outcome.action.action_id} does not match attempt action {attempt.action_id}"
        )
    checkpoint = attempt.before_checkpoint
    if not run.project_id == checkpoint.project_id == decision.project_id:
        raise ValueError(
            f"project mismatch: run {run.project_id}, checkpoint {checkpoint.project_id}, decision {decision.project_id}"
        )
    if decision.expected_revision != checkpoint.revision:
        raise ValueError(f"decision expects revision {decision.expected_revision}, checkpoint is {checkpoint.revision}")
    configuration = run.configuration
    context = configuration.context
    if decision.context_id != context.context_id or decision.context_version != context.version:
        raise ValueError("decision context does not match the run configuration")
    if decision.controller != configuration.controller:
        raise ValueError("decision controller does not match the run configuration")
    run_tracks = set(configuration.scope.track_ids)
    for artifact in checkpoint.artifacts:
        outside = sorted(str(t) for t in set(artifact.source_track_ids) - run_tracks)
        if outside:
            raise ValueError(
                f"checkpoint artifact {artifact.artifact_id} uses tracks outside the run scope: {', '.join(outside)}"
            )
    if attempt.validation is not None:
        validate_validation_references(attempt.validation, configuration.criteria)
