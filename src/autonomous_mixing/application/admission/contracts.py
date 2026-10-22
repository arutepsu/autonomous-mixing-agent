"""Admission request and result records."""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.application.admission.policy import ActionAdmissionPolicy
from autonomous_mixing.application.decision import DecisionRequest
from autonomous_mixing.domain.action import Action
from autonomous_mixing.domain.decision import Decision
from autonomous_mixing.domain.shared import DecisionId, VersionRef, require_instance, require_text


@dataclass(frozen=True)
class ActionAdmissionRequest:
    """Inputs for admission. Construction checks field types only; references are assessed by ``admit_action``."""

    decision_request: DecisionRequest
    decision: Decision
    policy: ActionAdmissionPolicy

    def __post_init__(self) -> None:
        require_instance(self.decision_request, DecisionRequest, "ActionAdmissionRequest.decision_request")
        require_instance(self.decision, Decision, "ActionAdmissionRequest.decision")
        require_instance(self.policy, ActionAdmissionPolicy, "ActionAdmissionRequest.policy")


class AdmissionRejectionCode(Enum):
    INVALID_REFERENCES = "invalid_references"
    POLICY_PROJECT_MISMATCH = "policy_project_mismatch"
    NOT_AN_ACTION = "not_an_action"  # e.g. a valid abstention: nothing to admit, not a run failure
    PROTECTED_TRACK = "protected_track"
    NO_GAIN_PERMISSION = "no_gain_permission"
    OUT_OF_BOUNDS = "out_of_bounds"


@dataclass(frozen=True)
class AdmittedAction:
    """A proposal that passed admission; not an execution receipt or security token."""

    action: Action
    policy_reference: VersionRef

    def __post_init__(self) -> None:
        require_instance(self.action, Action, "AdmittedAction.action")
        require_instance(self.policy_reference, VersionRef, "AdmittedAction.policy_reference")


@dataclass(frozen=True)
class RejectedAction:
    decision_id: DecisionId
    code: AdmissionRejectionCode
    explanation: str

    def __post_init__(self) -> None:
        require_instance(self.decision_id, DecisionId, "RejectedAction.decision_id")
        require_instance(self.code, AdmissionRejectionCode, "RejectedAction.code")
        require_text(self.explanation, "RejectedAction.explanation")


AdmissionResult = AdmittedAction | RejectedAction
