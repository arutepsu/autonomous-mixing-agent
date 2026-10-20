"""Typed action proposals.

An Action is proposal vocabulary, not permission to execute. Capability checks, producer
protections, parameter bounds and current-state checks belong to later application
enforcement; action types and bounds remain open decision D5.
"""

from dataclasses import dataclass

from autonomous_mixing.domain.action.operations import SetTrackGain
from autonomous_mixing.domain.shared import (
    ActionId,
    ProjectId,
    Revision,
    require_instance,
)


@dataclass(frozen=True)
class Action:
    action_id: ActionId
    project_id: ProjectId
    expected_revision: Revision
    operation: SetTrackGain

    def __post_init__(self) -> None:
        require_instance(self.action_id, ActionId, "Action.action_id")
        require_instance(self.project_id, ProjectId, "Action.project_id")
        require_instance(self.expected_revision, Revision, "Action.expected_revision")
        require_instance(self.operation, SetTrackGain, "Action.operation")
