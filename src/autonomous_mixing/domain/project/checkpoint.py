"""Artifact membership of one project state (candidate or accepted).

Artifact provenance (production revision) is kept separate from state membership: unchanged
artifacts are retained in later states, never retagged.
"""

from dataclasses import dataclass

from autonomous_mixing.domain.project.artifacts import AudioArtifact
from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.shared import (
    ArtifactId,
    CheckpointId,
    ProjectId,
    Revision,
    require_instance,
    require_tuple_of,
)


def _require_unique_artifacts(artifacts: tuple[AudioArtifact, ...], field: str, *, nonempty: bool) -> None:
    require_tuple_of(artifacts, AudioArtifact, field, nonempty=nonempty, distinct=False)
    ids = [artifact.artifact_id for artifact in artifacts]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field} must have unique artifact IDs")


@dataclass(frozen=True)
class ArtifactCheckpoint:
    """Artifact membership of one project state (stems, groups and/or mixes).

    ``revision`` identifies the represented project state. Member artifacts keep their own
    production revisions, which may be earlier than the state revision. A checkpoint may
    describe a candidate or an accepted state; its existence alone does not establish
    acceptance. Complete project coverage is not required, and one artifact per track is not
    assumed.
    """

    checkpoint_id: CheckpointId
    project_id: ProjectId
    revision: Revision
    artifacts: tuple[AudioArtifact, ...]

    def __post_init__(self) -> None:
        require_instance(self.checkpoint_id, CheckpointId, "ArtifactCheckpoint.checkpoint_id")
        require_instance(self.project_id, ProjectId, "ArtifactCheckpoint.project_id")
        require_instance(self.revision, Revision, "ArtifactCheckpoint.revision")
        _require_unique_artifacts(self.artifacts, "ArtifactCheckpoint.artifacts", nonempty=True)
        for artifact in self.artifacts:
            if artifact.project_id != self.project_id:
                raise ValueError(
                    f"checkpoint artifact {artifact.artifact_id} belongs to project {artifact.project_id}, "
                    f"not {self.project_id}"
                )

    @property
    def artifact_ids(self) -> frozenset[ArtifactId]:
        return frozenset(artifact.artifact_id for artifact in self.artifacts)

    @property
    def known_revisions(self) -> frozenset[Revision]:
        """Revisions visible in this membership: the state revision and every member's production revision.

        Local collision detection only; it knows nothing about fixed baselines or unseen history.
        """
        return frozenset({self.revision, *(artifact.revision for artifact in self.artifacts)})

    def artifact_for(self, artifact_id: ArtifactId) -> AudioArtifact | None:
        """Return the recorded member with this ID, or ``None`` if it is not a member."""
        for artifact in self.artifacts:
            if artifact.artifact_id == artifact_id:
                return artifact
        return None

    def validate_against(self, snapshot: ProjectSnapshot) -> None:
        """Require the represented state to be the snapshot's project state and known tracks only."""
        if self.project_id != snapshot.project_id:
            raise ValueError(f"checkpoint project {self.project_id} does not match snapshot {snapshot.project_id}")
        if self.revision != snapshot.revision:
            raise ValueError(f"checkpoint state revision {self.revision} does not match snapshot {snapshot.revision}")
        for artifact in self.artifacts:
            snapshot.require_known_tracks(artifact.source_track_ids, f"checkpoint artifact {artifact.artifact_id}")
