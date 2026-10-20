"""Observation records and their measured or explicitly unavailable results.

No metrics, analyzers, thresholds or confidence scores are defined here. A non-empty unit
string does not establish compatibility with any future metric catalog.
"""

from dataclasses import dataclass
from datetime import datetime

from autonomous_mixing.domain.project import AnalysisScope
from autonomous_mixing.domain.shared import (
    ArtifactId,
    ObservationId,
    VersionRef,
    require_finite,
    require_instance,
    require_text,
    require_tuple_of,
    require_utc,
)


@dataclass(frozen=True)
class MeasuredScalar:
    value: float
    unit: str

    def __post_init__(self) -> None:
        require_finite(self.value, "MeasuredScalar.value")
        require_text(self.unit, "MeasuredScalar.unit")


@dataclass(frozen=True)
class Unavailable:
    """An explicitly missing measurement; never a substitute for zero."""

    reason: str

    def __post_init__(self) -> None:
        require_text(self.reason, "Unavailable.reason")


@dataclass(frozen=True)
class Observation:
    observation_id: ObservationId
    metric: VersionRef
    artifact_ids: tuple[ArtifactId, ...]
    scope: AnalysisScope
    result: MeasuredScalar | Unavailable
    analysis_spec: VersionRef
    analyzer: VersionRef
    created_at: datetime

    def __post_init__(self) -> None:
        require_instance(self.observation_id, ObservationId, "Observation.observation_id")
        require_instance(self.metric, VersionRef, "Observation.metric")
        require_tuple_of(self.artifact_ids, ArtifactId, "Observation.artifact_ids", nonempty=True, distinct=True)
        require_instance(self.scope, AnalysisScope, "Observation.scope")
        require_instance(self.result, (MeasuredScalar, Unavailable), "Observation.result")
        require_instance(self.analysis_spec, VersionRef, "Observation.analysis_spec")
        require_instance(self.analyzer, VersionRef, "Observation.analyzer")
        require_utc(self.created_at, "Observation.created_at")
