"""Provenance check linking observations to members of an observed project state."""

from collections.abc import Iterable

from autonomous_mixing.domain.observation.observation import Observation
from autonomous_mixing.domain.project import ArtifactCheckpoint, AudioArtifact, ProjectSnapshot
from autonomous_mixing.domain.shared import (
    ArtifactId,
    TrackId,
    require_instance,
)


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
