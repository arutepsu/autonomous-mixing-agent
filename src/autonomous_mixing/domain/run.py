"""Run configuration, lifecycle state, budget, terminal-outcome and correction-attempt records.

``Run`` is an immutable record, not an executable state machine: legal transitions depend on
attempt and mutation-state contracts that are not defined yet. Budgets are recorded here and
enforced by a future coordinator.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from autonomous_mixing.domain.context import MusicalContext
from autonomous_mixing.domain.decision import ControllerIdentity, Decision, ProposeAction
from autonomous_mixing.domain.execution import (
    ArtifactCheckpoint,
    ExecutionReceipt,
    ExecutionStatus,
    RollbackReceipt,
    RollbackStatus,
    validate_receipt_against_checkpoint,
    validate_rollback_references,
)
from autonomous_mixing.domain.observation import AnalysisSpec, RenderSpec
from autonomous_mixing.domain.project import AnalysisScope, ProjectSnapshot
from autonomous_mixing.domain.validation import (
    AssessmentMode,
    ValidationCriteria,
    ValidationResult,
    ValidationVerdict,
    validate_validation_references,
)
from autonomous_mixing.domain.values import (
    ActionId,
    AttemptId,
    DecisionId,
    ProjectId,
    Revision,
    RunId,
    require_count,
    require_finite,
    require_instance,
    require_text,
    require_utc,
)


class RunState(Enum):
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    DECIDING = "deciding"
    CHECKING_ACTION = "checking_action"
    PREPARING_EXECUTION = "preparing_execution"
    EXECUTING = "executing"
    RECONCILING = "reconciling"
    ANALYZING_RESULT = "analyzing_result"
    VALIDATING = "validating"
    RESTORING = "restoring"
    FINISHED = "finished"


class RunOutcome(Enum):
    SUCCEEDED = "succeeded"
    ABSTAINED = "abstained"
    LIMIT_REACHED = "limit_reached"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FinalProjectState(Enum):
    """Disposition of project outputs at the end of a run, reported separately from the run outcome."""

    UNCHANGED = "unchanged"
    ACCEPTED_EDITS_RETAINED = "accepted_edits_retained"
    RESTORED_TO_LAST_ACCEPTED = "restored_to_last_accepted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BudgetLimits:
    """Configured resource limits. Zero count limits are valid (e.g. observe without attempting)."""

    max_decision_calls: int
    max_attempts: int
    max_render_calls: int
    max_recovery_operations: int
    max_elapsed_seconds: float

    def __post_init__(self) -> None:
        require_count(self.max_decision_calls, "BudgetLimits.max_decision_calls", minimum=0)
        require_count(self.max_attempts, "BudgetLimits.max_attempts", minimum=0)
        require_count(self.max_render_calls, "BudgetLimits.max_render_calls", minimum=0)
        require_count(self.max_recovery_operations, "BudgetLimits.max_recovery_operations", minimum=0)
        if require_finite(self.max_elapsed_seconds, "BudgetLimits.max_elapsed_seconds") <= 0:
            raise ValueError("BudgetLimits.max_elapsed_seconds must be strictly positive")


@dataclass(frozen=True)
class BudgetUsage:
    """Recorded resource use. Values beyond the configured limits are representable, so overruns stay visible."""

    decision_calls: int
    attempts: int
    render_calls: int
    recovery_operations: int
    elapsed_seconds: float

    def __post_init__(self) -> None:
        require_count(self.decision_calls, "BudgetUsage.decision_calls", minimum=0)
        require_count(self.attempts, "BudgetUsage.attempts", minimum=0)
        require_count(self.render_calls, "BudgetUsage.render_calls", minimum=0)
        require_count(self.recovery_operations, "BudgetUsage.recovery_operations", minimum=0)
        if require_finite(self.elapsed_seconds, "BudgetUsage.elapsed_seconds") < 0:
            raise ValueError("BudgetUsage.elapsed_seconds must be non-negative")


@dataclass(frozen=True)
class RunConfiguration:
    """Fixed run configuration, embedded as immutable values rather than a reference to a mutable file."""

    scope: AnalysisScope
    analysis_spec: AnalysisSpec
    render_spec: RenderSpec
    context: MusicalContext
    criteria: ValidationCriteria
    controller: ControllerIdentity
    budget_limits: BudgetLimits

    def __post_init__(self) -> None:
        require_instance(self.scope, AnalysisScope, "RunConfiguration.scope")
        require_instance(self.analysis_spec, AnalysisSpec, "RunConfiguration.analysis_spec")
        require_instance(self.render_spec, RenderSpec, "RunConfiguration.render_spec")
        require_instance(self.context, MusicalContext, "RunConfiguration.context")
        require_instance(self.criteria, ValidationCriteria, "RunConfiguration.criteria")
        require_instance(self.controller, ControllerIdentity, "RunConfiguration.controller")
        require_instance(self.budget_limits, BudgetLimits, "RunConfiguration.budget_limits")

    def validate_against(self, snapshot: ProjectSnapshot) -> None:
        """Check structural references and scope containment.

        Condition scopes may be subsets of the run scope. This does not check scientific validity,
        audio alignment, threshold calibration or metric/unit compatibility.
        """
        self.scope.validate_against(snapshot)
        self.context.validate_against(snapshot)
        run_tracks = set(self.scope.track_ids)
        run_time = self.scope.time_range
        run_band = self.scope.frequency_range
        nyquist_hz = self.render_spec.nyquist_hz
        if run_band is not None and run_band.high_hz > nyquist_hz:
            raise ValueError(f"run scope frequency {run_band.high_hz} Hz exceeds render Nyquist {nyquist_hz} Hz")
        criteria = self.criteria
        for condition in (*criteria.targets, *criteria.improvements, *criteria.guards):
            name = condition.condition_id
            selector = condition.selector
            selector.scope.validate_against(snapshot)
            outside = sorted(str(t) for t in set(selector.scope.track_ids) - run_tracks)
            if outside:
                raise ValueError(f"condition {name} uses tracks outside the run scope: {', '.join(outside)}")
            time = selector.scope.time_range
            if time.start_seconds < run_time.start_seconds or time.end_seconds > run_time.end_seconds:
                raise ValueError(f"condition {name} time range lies outside the run scope")
            band = selector.scope.frequency_range
            if run_band is not None:
                if band is None:
                    raise ValueError(f"condition {name} needs an explicit frequency range within the run scope")
                if band.low_hz < run_band.low_hz or band.high_hz > run_band.high_hz:
                    raise ValueError(f"condition {name} frequency range lies outside the run scope")
            if band is not None and band.high_hz > nyquist_hz:
                raise ValueError(f"condition {name} frequency {band.high_hz} Hz exceeds render Nyquist {nyquist_hz} Hz")
            if selector.metric not in self.analysis_spec.metric_ids:
                raise ValueError(
                    f"condition {name} metric {selector.metric.name}@{selector.metric.version} "
                    "is not listed in the analysis spec"
                )


@dataclass(frozen=True)
class Run:
    """Immutable run record. FINISHED runs carry all terminal fields; active runs carry none."""

    run_id: RunId
    project_id: ProjectId
    configuration: RunConfiguration
    initial_revision: Revision
    created_at: datetime
    state: RunState
    usage: BudgetUsage
    outcome: RunOutcome | None
    final_project_state: FinalProjectState | None
    termination_reason: str | None

    def __post_init__(self) -> None:
        require_instance(self.run_id, RunId, "Run.run_id")
        require_instance(self.project_id, ProjectId, "Run.project_id")
        require_instance(self.configuration, RunConfiguration, "Run.configuration")
        require_instance(self.initial_revision, Revision, "Run.initial_revision")
        require_utc(self.created_at, "Run.created_at")
        require_instance(self.state, RunState, "Run.state")
        require_instance(self.usage, BudgetUsage, "Run.usage")

        if self.state is RunState.FINISHED:
            require_instance(self.outcome, RunOutcome, "Run.outcome")
            require_instance(self.final_project_state, FinalProjectState, "Run.final_project_state")
            require_text(self.termination_reason, "Run.termination_reason")
            if self.outcome is RunOutcome.SUCCEEDED and self.final_project_state is FinalProjectState.UNKNOWN:
                raise ValueError("SUCCEEDED run cannot have UNKNOWN final project state")
        elif (self.outcome, self.final_project_state, self.termination_reason) != (None, None, None):
            raise ValueError(f"run in state {self.state.name} must not have terminal fields")


class AttemptDisposition(Enum):
    PENDING = "pending"  # partial records while processing is in progress; not permission to execute
    ACCEPTED = "accepted"
    ROLLED_BACK = "rolled_back"  # restoration of the before checkpoint is verified
    FAILED = "failed"  # known unsuccessful attempt (not started or failed execution), nothing to restore
    UNRESOLVED = "unresolved"  # execution or restoration cannot be established


@dataclass(frozen=True)
class CorrectionAttempt:
    """One attempted correction: its decision, execution, validation and rollback evidence.

    Construction checks consistency among the embedded records only. Run membership, decision
    identity, criteria and complete artifact provenance need external objects and are checked by
    ``validate_attempt_references``.
    """

    attempt_id: AttemptId
    run_id: RunId
    decision_id: DecisionId
    action_id: ActionId
    before_checkpoint: ArtifactCheckpoint
    execution: ExecutionReceipt | None
    validation: ValidationResult | None
    rollback: RollbackReceipt | None
    disposition: AttemptDisposition

    def __post_init__(self) -> None:
        require_instance(self.attempt_id, AttemptId, "CorrectionAttempt.attempt_id")
        require_instance(self.run_id, RunId, "CorrectionAttempt.run_id")
        require_instance(self.decision_id, DecisionId, "CorrectionAttempt.decision_id")
        require_instance(self.action_id, ActionId, "CorrectionAttempt.action_id")
        require_instance(self.before_checkpoint, ArtifactCheckpoint, "CorrectionAttempt.before_checkpoint")
        if self.execution is not None:
            require_instance(self.execution, ExecutionReceipt, "CorrectionAttempt.execution")
        if self.validation is not None:
            require_instance(self.validation, ValidationResult, "CorrectionAttempt.validation")
        if self.rollback is not None:
            require_instance(self.rollback, RollbackReceipt, "CorrectionAttempt.rollback")
        require_instance(self.disposition, AttemptDisposition, "CorrectionAttempt.disposition")

        execution, checkpoint = self.execution, self.before_checkpoint
        status = execution.status if execution is not None else None
        if execution is not None:
            if execution.action_id != self.action_id:
                raise ValueError(f"execution action {execution.action_id} does not match attempt {self.action_id}")
            # Project, before revision, superseded membership and no candidate-ID reuse.
            validate_receipt_against_checkpoint(execution, checkpoint)
        if self.validation is not None:
            if status is not ExecutionStatus.CANDIDATE_READY:
                raise ValueError("validation requires a CANDIDATE_READY execution")
            # An INITIAL assessment describes the starting state and is never evidence for an attempt.
            if self.validation.mode is not AssessmentMode.ATTEMPT:
                raise ValueError("attempt validation must be an ATTEMPT assessment, not an INITIAL assessment")
        if self.rollback is not None:
            if execution is None:
                raise ValueError("rollback evidence requires an execution receipt")
            if self.rollback.execution_id != execution.execution_id:
                raise ValueError(
                    f"rollback refers to execution {self.rollback.execution_id}, not {execution.execution_id}"
                )
            validate_rollback_references(self.rollback, checkpoint)
        rollback_status = self.rollback.status if self.rollback is not None else None

        disposition = self.disposition
        if disposition is AttemptDisposition.ACCEPTED:
            if status is not ExecutionStatus.CANDIDATE_READY:
                raise ValueError("ACCEPTED attempt requires a CANDIDATE_READY execution")
            if self.validation is None or self.validation.verdict is not ValidationVerdict.ACCEPTED:
                raise ValueError("ACCEPTED attempt requires an ACCEPTED validation verdict")
            if self.rollback is not None:
                raise ValueError("ACCEPTED attempt must not carry rollback evidence")
        elif disposition is AttemptDisposition.ROLLED_BACK:
            if rollback_status is not RollbackStatus.VERIFIED:
                raise ValueError("ROLLED_BACK attempt requires a VERIFIED rollback receipt")
        elif disposition is AttemptDisposition.FAILED:
            if status not in (ExecutionStatus.NOT_STARTED, ExecutionStatus.FAILED):
                raise ValueError("FAILED attempt requires a NOT_STARTED or FAILED execution")
            if self.rollback is not None:
                raise ValueError("FAILED attempt must not carry rollback evidence")
        elif disposition is AttemptDisposition.UNRESOLVED:
            unsuccessful_rollback = rollback_status in (RollbackStatus.FAILED, RollbackStatus.UNCERTAIN)
            if status is not ExecutionStatus.UNCERTAIN and not unsuccessful_rollback:
                raise ValueError("UNRESOLVED attempt requires uncertain execution or failed/uncertain rollback")


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
