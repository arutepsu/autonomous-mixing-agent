"""Port for requesting a decision from a controller."""

from typing import Protocol

from autonomous_mixing.application.contracts import DecisionRequest, DecisionResponse
from autonomous_mixing.application.results import PortResult


class DecisionController(Protocol):
    """Proposes one action or an abstention for a decision request.

    Implementations return expected failures as ``PortFailure``; callers validate successful
    responses with ``validate_decision_response``. A response is a proposal, not permission to
    execute.
    """

    def decide(self, request: DecisionRequest) -> PortResult[DecisionResponse]: ...
