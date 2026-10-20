"""Shared domain primitives: typed identifiers, version references and invariant helpers.

These helpers are an intentional public interface for domain and application input boundaries.
"""

from autonomous_mixing.domain.shared.identifiers import (
    ActionId,
    ArtifactId,
    AttemptId,
    CheckpointId,
    ConditionId,
    ContextId,
    CriteriaId,
    DecisionId,
    ExecutionId,
    ObservationId,
    ProjectId,
    Revision,
    RunId,
    TrackId,
    ValidationResultId,
)
from autonomous_mixing.domain.shared.invariants import (
    require_count,
    require_finite,
    require_finite_result,
    require_instance,
    require_text,
    require_tuple_of,
    require_utc,
)
from autonomous_mixing.domain.shared.versions import VersionRef

__all__ = [
    "ProjectId",
    "TrackId",
    "ArtifactId",
    "ObservationId",
    "ContextId",
    "ActionId",
    "DecisionId",
    "CriteriaId",
    "ConditionId",
    "ValidationResultId",
    "RunId",
    "AttemptId",
    "ExecutionId",
    "CheckpointId",
    "Revision",
    "VersionRef",
    "require_text",
    "require_finite",
    "require_finite_result",
    "require_count",
    "require_utc",
    "require_instance",
    "require_tuple_of",
]
