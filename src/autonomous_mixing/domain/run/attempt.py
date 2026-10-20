"""Correction attempts linking decision, execution, validation and rollback evidence."""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.action import (
    ExecutionReceipt,
    ExecutionStatus,
    RollbackReceipt,
    RollbackStatus,
    validate_receipt_against_checkpoint,
    validate_rollback_references,
)
from autonomous_mixing.domain.project import ArtifactCheckpoint
from autonomous_mixing.domain.shared import (
    ActionId,
    AttemptId,
    DecisionId,
    RunId,
    require_instance,
)
from autonomous_mixing.domain.validation import AssessmentMode, ValidationResult, ValidationVerdict


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
