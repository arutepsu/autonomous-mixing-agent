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

from autonomous_mixing.application.admission.contracts import (
    ActionAdmissionRequest,
    AdmissionRejectionCode,
    AdmissionResult,
    AdmittedAction,
    RejectedAction,
)
from autonomous_mixing.application.admission.policy import ActionAdmissionPolicy, TrackGainPermission
from autonomous_mixing.application.decision import DecisionResponse, validate_decision_response
from autonomous_mixing.domain.decision import ProposeAction
from autonomous_mixing.domain.shared import TrackId, require_instance


def _gain_permission_for(policy: ActionAdmissionPolicy, track_id: TrackId) -> TrackGainPermission | None:
    for permission in policy.gain_permissions:
        if permission.track_id == track_id:
            return permission
    return None


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
