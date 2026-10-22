"""Request/response records for the decision port.

Requests carry one composite ``ProjectState`` (ADR-019), so callers cannot pair a snapshot with audio
from another state. These contracts check structure and provenance only: not budgets, execution
permissions or musical appropriateness. The decision request is not the complete future controller
input: problem candidates (FR-05, D11), action capabilities and permitted actions (D5), attempt
history and raw provider responses are deferred contracts. Hidden evaluation data never belongs in
these records (SR-10).
"""

from dataclasses import dataclass

from autonomous_mixing.domain.context import MusicalContext
from autonomous_mixing.domain.decision import ControllerIdentity, Decision
from autonomous_mixing.domain.observation import Observation, validate_observation_sources
from autonomous_mixing.domain.project import ProjectState
from autonomous_mixing.domain.run import BudgetLimits, BudgetUsage
from autonomous_mixing.domain.shared import require_instance, require_tuple_of


def _require_unique_observations(observations: tuple[Observation, ...], field: str) -> None:
    # Decision's own copy of the observation component's private check (same check and messages), so
    # decision does not depend on observation. Consolidating validation semantics is a separate task.
    require_tuple_of(observations, Observation, field, nonempty=False, distinct=False)
    ids = [observation.observation_id for observation in observations]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field} must have unique observation IDs")


@dataclass(frozen=True)
class DecisionRequest:
    """Runtime-visible inputs for one decision.

    Usage may exceed limits (the record describes, it does not enforce). Artifact locations are
    ordinary runtime source references; this record alone does not sandbox a provider.
    """

    state: ProjectState
    context: MusicalContext
    controller: ControllerIdentity
    observations: tuple[Observation, ...]
    usage: BudgetUsage
    limits: BudgetLimits

    def __post_init__(self) -> None:
        require_instance(self.state, ProjectState, "DecisionRequest.state")
        require_instance(self.context, MusicalContext, "DecisionRequest.context")
        require_instance(self.controller, ControllerIdentity, "DecisionRequest.controller")
        _require_unique_observations(self.observations, "DecisionRequest.observations")
        require_instance(self.usage, BudgetUsage, "DecisionRequest.usage")
        require_instance(self.limits, BudgetLimits, "DecisionRequest.limits")
        snapshot, audio = self.state.snapshot, self.state.audio
        self.context.validate_against(snapshot)
        for observation in self.observations:
            validate_observation_sources(observation, audio.artifacts, audio, snapshot)


@dataclass(frozen=True)
class DecisionResponse:
    decision: Decision

    def __post_init__(self) -> None:
        require_instance(self.decision, Decision, "DecisionResponse.decision")
