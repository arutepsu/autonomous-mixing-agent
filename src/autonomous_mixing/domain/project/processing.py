"""Explicit per-track gain processing state relative to fixed runtime input artifacts.

``gain_db`` is absolute additional gain applied to the track's fixed ``input_artifact``: setting
-3 dB twice means -3 dB in total, and 0 dB means the input level (including any effects already
baked into that input). It is never a delta applied to the latest output. A track without a gain
state is unrepresented, never implicitly 0 dB. These records model parameters only; they do not
render audio or prove that rendered files reflect them.
"""

from dataclasses import dataclass

from autonomous_mixing.domain.project.artifacts import ArtifactKind, AudioArtifact
from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.shared import (
    ArtifactId,
    ProjectId,
    Revision,
    TrackId,
    require_finite,
    require_instance,
    require_tuple_of,
)


@dataclass(frozen=True)
class TrackGainState:
    """Absolute additional gain (dB) for one track relative to its fixed input stem. No default or bounds."""

    track_id: TrackId
    input_artifact: AudioArtifact
    gain_db: float

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "TrackGainState.track_id")
        require_instance(self.input_artifact, AudioArtifact, "TrackGainState.input_artifact")
        require_finite(self.gain_db, "TrackGainState.gain_db")
        if self.input_artifact.kind is not ArtifactKind.STEM:
            raise ValueError(f"fixed input {self.input_artifact.artifact_id} must be a STEM artifact")
        if self.input_artifact.source_track_ids != (self.track_id,):
            raise ValueError(
                f"fixed input {self.input_artifact.artifact_id} must be a stem of exactly track {self.track_id}"
            )


@dataclass(frozen=True)
class ProjectProcessingState:
    """Gain settings of one project state. Coverage may be partial or empty; absent tracks are unrepresented."""

    project_id: ProjectId
    revision: Revision
    track_gains: tuple[TrackGainState, ...]

    def __post_init__(self) -> None:
        require_instance(self.project_id, ProjectId, "ProjectProcessingState.project_id")
        require_instance(self.revision, Revision, "ProjectProcessingState.revision")
        require_tuple_of(
            self.track_gains, TrackGainState, "ProjectProcessingState.track_gains", nonempty=False, distinct=False
        )
        tracks = [gain.track_id for gain in self.track_gains]
        if len(set(tracks)) != len(tracks):
            raise ValueError("ProjectProcessingState.track_gains must have unique track IDs")
        inputs: dict[ArtifactId, AudioArtifact] = {}
        for gain in self.track_gains:
            artifact = gain.input_artifact
            if artifact.project_id != self.project_id:
                raise ValueError(
                    f"fixed input {artifact.artifact_id} belongs to project {artifact.project_id}, not {self.project_id}"
                )
            recorded = inputs.setdefault(artifact.artifact_id, artifact)
            if recorded != artifact:
                raise ValueError(f"fixed input {artifact.artifact_id} is described with conflicting metadata")

    def validate_against(self, snapshot: ProjectSnapshot) -> None:
        """Require the snapshot's project and state revision and known tracks; no file or capability checks."""
        if self.project_id != snapshot.project_id:
            raise ValueError(f"processing project {self.project_id} does not match snapshot {snapshot.project_id}")
        if self.revision != snapshot.revision:
            raise ValueError(f"processing state revision {self.revision} does not match snapshot {snapshot.revision}")
        snapshot.require_known_tracks(tuple(gain.track_id for gain in self.track_gains), "ProjectProcessingState")
