"""Compatibility shim: re-exports shared primitives from ``autonomous_mixing.domain.shared``.

Deprecated import location kept for existing callers; new code imports from
``autonomous_mixing.domain.shared``. Contains no definitions of its own.
"""

from autonomous_mixing.domain.shared import (
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
    VersionRef,
    require_count,
    require_finite,
    require_finite_result,
    require_instance,
    require_text,
    require_tuple_of,
    require_utc,
)

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
