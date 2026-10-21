"""Explicit admission policy for proposed gain actions (partial enforcement groundwork).

``admit_action`` deterministically admits or rejects a proposed action against configured
per-track absolute gain bounds and producer protections. It never clamps, rounds or infers
permission from track names, roles, observation scopes or the mere existence of a track.

Limits of this check:
- An ``AdmittedAction`` is a checked proposal, not an execution receipt, permission token or
  security boundary; no execution service exists yet.
- Permissions describe configured authorization, not that a future executor supports the
  operation or track.
- The expected revision is checked against the supplied state's snapshot only. That does not prove the
  external project state is still current; a future executor must recheck immediately before
  mutation.
- The requested value is compared with configured absolute bounds only; its meaning relative to
  audio (current gain, deltas, cumulative movement) is not interpreted here.
- Budgets, capabilities, evidence sufficiency and musical appropriateness are not assessed.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.application.contracts import DecisionRequest, DecisionResponse, validate_decision_response
from autonomous_mixing.domain.action import Action
from autonomous_mixing.domain.decision import Decision, ProposeAction
from autonomous_mixing.domain.shared import (
    DecisionId,
    ProjectId,
    TrackId,
    VersionRef,
    require_finite,
    require_instance,
    require_text,
    require_tuple_of,
)


@dataclass(frozen=True)
class TrackGainPermission:
    """Configured absolute gain range for one track, in dB, inclusive at both ends.

    No default or scientifically motivated limits are implied; equal bounds permit one exact setting.
    """

    track_id: TrackId
    minimum_db: float
    maximum_db: float

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "TrackGainPermission.track_id")
        minimum = require_finite(self.minimum_db, "TrackGainPermission.minimum_db")
        maximum = require_finite(self.maximum_db, "TrackGainPermission.maximum_db")
        if minimum > maximum:
            raise ValueError(f"TrackGainPermission.minimum_db {minimum} exceeds maximum_db {maximum}")


@dataclass(frozen=True)
class ActionAdmissionPolicy:
    """Versioned admission configuration for one project. Empty permissions deny every gain action."""

    reference: VersionRef
    project_id: ProjectId
    gain_permissions: tuple[TrackGainPermission, ...]

    def __post_init__(self) -> None:
        require_instance(self.reference, VersionRef, "ActionAdmissionPolicy.reference")
        require_instance(self.project_id, ProjectId, "ActionAdmissionPolicy.project_id")
        require_tuple_of(
            self.gain_permissions,
            TrackGainPermission,
            "ActionAdmissionPolicy.gain_permissions",
            nonempty=False,
            distinct=False,
        )
        tracks = [permission.track_id for permission in self.gain_permissions]
        if len(set(tracks)) != len(tracks):
            raise ValueError("ActionAdmissionPolicy.gain_permissions must have at most one permission per track")


def _gain_permission_for(policy: ActionAdmissionPolicy, track_id: TrackId) -> TrackGainPermission | None:
    for permission in policy.gain_permissions:
        if permission.track_id == track_id:
            return permission
    return None


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


def admit_action(request: ActionAdmissionRequest) -> AdmissionResult:
    """Admit or reject a decision's proposed action. Checks run in a fixed order; the first failure wins.

    1. decision references and controller (via ``validate_decision_response``), 2. policy project,
    3. a ProposeAction outcome, 4. producer protection, 5. an explicit gain permission, 6. inclusive bounds.
    """
    require_instance(request, ActionAdmissionRequest, "request")
    decision, decision_request, policy = request.decision, request.decision_request, request.policy

    def reject(code: AdmissionRejectionCode, explanation: str) -> RejectedAction:
        return RejectedAction(decision.decision_id, code, explanation)

    try:
        validate_decision_response(decision_request, DecisionResponse(decision))
    except ValueError as error:  # expected reference failures only; other exceptions propagate
        return reject(AdmissionRejectionCode.INVALID_REFERENCES, f"decision references are invalid: {error}")

    snapshot_project = decision_request.state.snapshot.project_id
    if policy.project_id != snapshot_project:
        return reject(
            AdmissionRejectionCode.POLICY_PROJECT_MISMATCH,
            f"policy {policy.reference.name}@{policy.reference.version} is for project {policy.project_id}, "
            f"not {snapshot_project}",
        )

    if not isinstance(decision.outcome, ProposeAction):
        return reject(AdmissionRejectionCode.NOT_AN_ACTION, "the decision does not propose an action")
    action = decision.outcome.action
    operation = action.operation  # SetTrackGain is the only operation type (enforced by Action)

    target = operation.track_id
    if target in decision_request.context.protected_track_ids:
        return reject(AdmissionRejectionCode.PROTECTED_TRACK, f"track {target} is protected by the producer context")

    permission = _gain_permission_for(policy, target)
    if permission is None:
        return reject(AdmissionRejectionCode.NO_GAIN_PERMISSION, f"policy grants no gain permission for track {target}")

    if not permission.minimum_db <= operation.value_db <= permission.maximum_db:
        return reject(
            AdmissionRejectionCode.OUT_OF_BOUNDS,
            f"requested gain {operation.value_db} dB for track {target} is outside the permitted range "
            f"[{permission.minimum_db}, {permission.maximum_db}] dB",
        )

    return AdmittedAction(action, policy.reference)
