"""Structural check of a decision response against its request."""

from autonomous_mixing.application.decision.contracts import DecisionRequest, DecisionResponse
from autonomous_mixing.domain.decision import validate_decision_references
from autonomous_mixing.domain.shared import require_instance


def validate_decision_response(request: DecisionRequest, response: DecisionResponse) -> None:
    """Check a decision's structural references and controller identity against its request."""
    require_instance(request, DecisionRequest, "request")
    require_instance(response, DecisionResponse, "response")
    decision = response.decision
    validate_decision_references(decision, request.state.snapshot, request.context, request.observations)
    if decision.controller != request.controller:
        raise ValueError(
            f"decision controller {decision.controller.name}@{decision.controller.version} does not match "
            f"the requested controller {request.controller.name}@{request.controller.version}"
        )
