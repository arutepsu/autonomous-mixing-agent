"""Observation records and their provenance links to audio artifacts.

No metrics, analyzers, thresholds or confidence scores are defined here. A non-empty unit
string does not establish compatibility with any future metric catalog.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from autonomous_mixing.domain.execution import ArtifactCheckpoint
from autonomous_mixing.domain.project import AnalysisScope, AudioArtifact, ProjectSnapshot
from autonomous_mixing.domain.values import (
    ArtifactId,
    ObservationId,
    TrackId,
    VersionRef,
    require_count,
    require_finite,
    require_finite_result,
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
class AnalysisSpec:
    ref: VersionRef
    metric_ids: tuple[VersionRef, ...]

    def __post_init__(self) -> None:
        require_instance(self.ref, VersionRef, "AnalysisSpec.ref")
        require_tuple_of(self.metric_ids, VersionRef, "AnalysisSpec.metric_ids", nonempty=True, distinct=True)


@dataclass(frozen=True)
class RenderSpec:
    """Render configuration data; not a renderer."""

    ref: VersionRef
    sample_rate_hz: int
    channel_count: int

    def __post_init__(self) -> None:
        require_instance(self.ref, VersionRef, "RenderSpec.ref")
        require_count(self.sample_rate_hz, "RenderSpec.sample_rate_hz", minimum=1)
        if require_count(self.channel_count, "RenderSpec.channel_count", minimum=1) > 2:
            raise ValueError(f"RenderSpec.channel_count must be 1 or 2, got {self.channel_count}")
        require_finite_result(lambda: self.nyquist_hz, "RenderSpec Nyquist frequency")

    @property
    def nyquist_hz(self) -> float:
        return self.sample_rate_hz / 2


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


def validate_observation_sources(
    observation: Observation,
    artifacts: Iterable[AudioArtifact],
    checkpoint: ArtifactCheckpoint,
    snapshot: ProjectSnapshot,
) -> None:
    """Check that an observation's sources belong to the observed state and cover its scope.

    The checkpoint names the project state (candidate or accepted) that was observed; it must
    match the snapshot's project and revision. Every referenced source must be a member of that
    checkpoint, and the supplied metadata must equal the recorded member. Source production
    revisions may differ from the state revision (unchanged artifacts are retained, not
    retagged). Coverage is derived from artifact metadata with exact comparisons; no resampling,
    offset adjustment or signal-alignment inference is made. Unreferenced artifacts are ignored.
    """
    checkpoint.validate_against(snapshot)
    by_id: dict[ArtifactId, AudioArtifact] = {}
    for artifact in artifacts:
        require_instance(artifact, AudioArtifact, "artifact")
        if artifact.artifact_id in by_id:
            raise ValueError(f"duplicate artifact ID supplied: {artifact.artifact_id}")
        by_id[artifact.artifact_id] = artifact

    missing = [str(a) for a in observation.artifact_ids if a not in by_id]
    if missing:
        raise ValueError(f"missing source artifacts: {', '.join(missing)}")
    sources = [by_id[a] for a in observation.artifact_ids]

    scope = observation.scope
    scope.validate_against(snapshot)
    covered: set[TrackId] = set()
    for artifact in sources:
        recorded = checkpoint.artifact_for(artifact.artifact_id)
        if recorded is None:
            raise ValueError(
                f"artifact {artifact.artifact_id} is not a member of checkpoint {checkpoint.checkpoint_id}"
            )
        if artifact != recorded:
            raise ValueError(
                f"artifact {artifact.artifact_id} metadata does not match its record in checkpoint "
                f"{checkpoint.checkpoint_id}"
            )
        snapshot.require_known_tracks(artifact.source_track_ids, f"artifact {artifact.artifact_id}")
        covered.update(artifact.source_track_ids)
        if (
            artifact.timeline_start_seconds > scope.time_range.start_seconds
            or artifact.timeline_end_seconds < scope.time_range.end_seconds
        ):
            raise ValueError(f"artifact {artifact.artifact_id} timeline does not cover the scope time range")
        if scope.frequency_range is not None and scope.frequency_range.high_hz > artifact.nyquist_hz:
            raise ValueError(
                f"scope frequency {scope.frequency_range.high_hz} Hz exceeds Nyquist of artifact {artifact.artifact_id}"
            )

    uncovered = [str(t) for t in scope.track_ids if t not in covered]
    if uncovered:
        raise ValueError(f"scope tracks not covered by source artifacts: {', '.join(uncovered)}")
