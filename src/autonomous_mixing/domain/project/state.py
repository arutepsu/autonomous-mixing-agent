"""Composite project state: snapshot, gain processing settings and rendered-audio membership."""

from dataclasses import dataclass

from autonomous_mixing.domain.project.checkpoint import ArtifactCheckpoint
from autonomous_mixing.domain.project.processing import ProjectProcessingState
from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.shared import ProjectId, Revision, require_instance


@dataclass(frozen=True)
class ProjectState:
    """One consistent project state; it may describe a candidate or an accepted state.

    Snapshot, processing and audio must share the project and state revision. Fixed input artifacts
    need not be current audio members (a superseded baseline must stay available to later
    execution); where an input ID is also an audio member, its metadata must match exactly.
    Constructing a state does not accept it, and structural consistency is not proof that rendered
    files reflect the parameter state. Availability, retention and integrity of artifacts are later
    adapter responsibilities.
    """

    snapshot: ProjectSnapshot
    processing: ProjectProcessingState
    audio: ArtifactCheckpoint

    def __post_init__(self) -> None:
        require_instance(self.snapshot, ProjectSnapshot, "ProjectState.snapshot")
        require_instance(self.processing, ProjectProcessingState, "ProjectState.processing")
        require_instance(self.audio, ArtifactCheckpoint, "ProjectState.audio")
        self.processing.validate_against(self.snapshot)
        self.audio.validate_against(self.snapshot)
        for gain in self.processing.track_gains:
            member = self.audio.artifact_for(gain.input_artifact.artifact_id)
            if member is not None and member != gain.input_artifact:
                raise ValueError(
                    f"fixed input {gain.input_artifact.artifact_id} differs from the audio member with the same ID"
                )

    @property
    def project_id(self) -> ProjectId:
        return self.snapshot.project_id

    @property
    def revision(self) -> Revision:
        return self.snapshot.revision

    @property
    def known_revisions(self) -> frozenset[Revision]:
        """Locally known revisions: the state revision, audio members' and fixed baselines' production revisions.

        A new candidate state must not reuse any of these. Local collision detection only: global
        uniqueness and revisions of unseen history need identity allocation and a ledger.
        """
        baselines = (gain.input_artifact.revision for gain in self.processing.track_gains)
        return self.audio.known_revisions | frozenset(baselines)
