"""Controller decisions: exactly one typed outcome, either a proposed action or an abstention.

Decisions carry no confidence score or executable callback. Problem candidates are not
represented yet (FR-05, D11).
"""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.action import Action
from autonomous_mixing.domain.context import MusicalContext
from autonomous_mixing.domain.observation import Observation
from autonomous_mixing.domain.project import ProjectSnapshot
from autonomous_mixing.domain.values import (
    ContextId,
    DecisionId,
    ObservationId,
    ProjectId,
    Revision,
    require_instance,
    require_text,
    require_tuple_of,
)


@dataclass(frozen=True)
class ControllerIdentity:
    name: str
    version: str

    def __post_init__(self) -> None:
        require_text(self.name, "ControllerIdentity.name")
        require_text(self.version, "ControllerIdentity.version")


@dataclass(frozen=True)
class ProposeAction:
    action: Action
    expected_effect: str

    def __post_init__(self) -> None:
        require_instance(self.action, Action, "ProposeAction.action")
        require_text(self.expected_effect, "ProposeAction.expected_effect")


class AbstentionReason(Enum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    MISSING_CONTEXT = "missing_context"
    CONFLICTING_CONSTRAINTS = "conflicting_constraints"
    NO_JUSTIFIED_ACTION = "no_justified_action"


@dataclass(frozen=True)
class Abstain:
    """An explicit decision not to act. ``requested_context`` explains what is missing; it does not pause a run."""

    reason: AbstentionReason
    requested_context: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_instance(self.reason, AbstentionReason, "Abstain.reason")
        require_tuple_of(self.requested_context, str, "Abstain.requested_context", nonempty=False, distinct=True)
        for entry in self.requested_context:
            require_text(entry, "Abstain.requested_context element")


@dataclass(frozen=True)
class Decision:
    decision_id: DecisionId
    project_id: ProjectId
    expected_revision: Revision
    context_id: ContextId
    context_version: str
    evidence_ids: tuple[ObservationId, ...]
    rationale: str
    controller: ControllerIdentity
    outcome: ProposeAction | Abstain

    def __post_init__(self) -> None:
        require_instance(self.decision_id, DecisionId, "Decision.decision_id")
        require_instance(self.project_id, ProjectId, "Decision.project_id")
        require_instance(self.expected_revision, Revision, "Decision.expected_revision")
        require_instance(self.context_id, ContextId, "Decision.context_id")
        require_text(self.context_version, "Decision.context_version")
        require_tuple_of(self.evidence_ids, ObservationId, "Decision.evidence_ids", nonempty=False, distinct=True)
        require_text(self.rationale, "Decision.rationale")
        require_instance(self.controller, ControllerIdentity, "Decision.controller")
        require_instance(self.outcome, (ProposeAction, Abstain), "Decision.outcome")
        if isinstance(self.outcome, ProposeAction):
            if not self.evidence_ids:
                raise ValueError("Decision proposing an action must reference at least one observation")
            action = self.outcome.action
            if action.project_id != self.project_id:
                raise ValueError(f"proposed action targets project {action.project_id}, decision {self.project_id}")
            if action.expected_revision != self.expected_revision:
                raise ValueError(
                    f"proposed action expects revision {action.expected_revision}, decision {self.expected_revision}"
                )


def validate_decision_references(
    decision: Decision,
    snapshot: ProjectSnapshot,
    context: MusicalContext,
    observations: Iterable[Observation],
) -> None:
    """Check a decision's structural references against a snapshot, context and observations.

    This does not verify source-audio provenance (use ``validate_observation_sources``), whether
    the evidence justifies the action, or any protection, capability or bound. Supplied
    observations not referenced by the decision are ignored.
    """
    if decision.project_id != snapshot.project_id:
        raise ValueError(f"decision project {decision.project_id} does not match snapshot {snapshot.project_id}")
    if decision.expected_revision != snapshot.revision:
        raise ValueError(f"decision expects revision {decision.expected_revision}, snapshot is {snapshot.revision}")
    if decision.context_id != context.context_id or decision.context_version != context.version:
        raise ValueError(
            f"decision context {decision.context_id}@{decision.context_version} does not match "
            f"supplied context {context.context_id}@{context.version}"
        )
    context.validate_against(snapshot)

    by_id: dict[ObservationId, Observation] = {}
    for observation in observations:
        require_instance(observation, Observation, "observation")
        if observation.observation_id in by_id:
            raise ValueError(f"duplicate observation ID supplied: {observation.observation_id}")
        by_id[observation.observation_id] = observation
    missing = [str(o) for o in decision.evidence_ids if o not in by_id]
    if missing:
        raise ValueError(f"missing referenced observations: {', '.join(missing)}")
    for observation_id in decision.evidence_ids:
        by_id[observation_id].scope.validate_against(snapshot)

    if isinstance(decision.outcome, ProposeAction):
        target = decision.outcome.action.operation.track_id
        snapshot.require_known_tracks((target,), "proposed action target")
