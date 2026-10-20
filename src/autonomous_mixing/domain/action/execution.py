"""Execution receipts and derivation of candidate state membership.

Processing writes separate candidate artifacts; acceptance changes which artifacts are
designated as accepted. These records are metadata: they do not prove that files exist,
match their hashes, or were cleaned up. Checkpoint membership is owned by the project
component; this module derives candidate membership from an execution receipt.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.project import (
    ArtifactCheckpoint,
    AudioArtifact,
)
from autonomous_mixing.domain.shared import (
    ActionId,
    ArtifactId,
    CheckpointId,
    ExecutionId,
    ProjectId,
    Revision,
    require_instance,
    require_text,
    require_tuple_of,
)


def _require_unique_artifacts(artifacts: tuple[AudioArtifact, ...], field: str, *, nonempty: bool) -> None:
    require_tuple_of(artifacts, AudioArtifact, field, nonempty=nonempty, distinct=False)
    ids = [artifact.artifact_id for artifact in artifacts]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field} must have unique artifact IDs")


class ExecutionStatus(Enum):
    NOT_STARTED = "not_started"
    FAILED = "failed"  # may leave temporary files; no cleanup is claimed
    CANDIDATE_READY = "candidate_ready"
    UNCERTAIN = "uncertain"  # the outcome cannot be established


@dataclass(frozen=True)
class ExecutionIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        require_text(self.code, "ExecutionIssue.code")
        require_text(self.message, "ExecutionIssue.message")


@dataclass(frozen=True)
class ExecutionReceipt:
    """Outcome of executing one action. Candidate artifacts are newly produced outputs only.

    ``superseded_artifact_ids`` explicitly names the before-state artifacts the candidates
    replace; replacement is never inferred. For the supported track-gain operation a
    CANDIDATE_READY receipt must supersede at least one artifact. Execution planning must list
    every affected derived artifact (e.g. groups and mixes containing an edited track); this
    record does not implement dependency invalidation. No status authorizes acceptance or
    another edit.
    """

    execution_id: ExecutionId
    action_id: ActionId
    project_id: ProjectId
    before_revision: Revision
    status: ExecutionStatus
    candidate_revision: Revision | None
    candidate_artifacts: tuple[AudioArtifact, ...]
    superseded_artifact_ids: tuple[ArtifactId, ...]
    issue: ExecutionIssue | None

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "ExecutionReceipt.execution_id")
        require_instance(self.action_id, ActionId, "ExecutionReceipt.action_id")
        require_instance(self.project_id, ProjectId, "ExecutionReceipt.project_id")
        require_instance(self.before_revision, Revision, "ExecutionReceipt.before_revision")
        require_instance(self.status, ExecutionStatus, "ExecutionReceipt.status")
        if self.candidate_revision is not None:
            require_instance(self.candidate_revision, Revision, "ExecutionReceipt.candidate_revision")
        _require_unique_artifacts(self.candidate_artifacts, "ExecutionReceipt.candidate_artifacts", nonempty=False)
        require_tuple_of(
            self.superseded_artifact_ids,
            ArtifactId,
            "ExecutionReceipt.superseded_artifact_ids",
            nonempty=False,
            distinct=True,
        )
        if self.issue is not None:
            require_instance(self.issue, ExecutionIssue, "ExecutionReceipt.issue")
        for artifact in self.candidate_artifacts:
            if artifact.project_id != self.project_id or artifact.revision != self.candidate_revision:
                raise ValueError(
                    f"candidate artifact {artifact.artifact_id} does not match project {self.project_id} "
                    f"and candidate revision {self.candidate_revision}"
                )

        status = self.status.name
        if self.status is ExecutionStatus.CANDIDATE_READY:
            if self.candidate_revision is None or self.candidate_revision == self.before_revision:
                raise ValueError("CANDIDATE_READY requires a candidate revision different from the before revision")
            if not self.candidate_artifacts:
                raise ValueError("CANDIDATE_READY requires candidate artifacts")
            if not self.superseded_artifact_ids:
                raise ValueError("CANDIDATE_READY requires explicit superseded artifact IDs")
            overlap = sorted(str(a) for a in set(self.superseded_artifact_ids) & self.candidate_artifact_ids)
            if overlap:
                raise ValueError(f"a candidate artifact cannot supersede itself: {', '.join(overlap)}")
            if self.issue is not None:
                raise ValueError("CANDIDATE_READY must not carry an issue")
            return
        if self.candidate_revision is not None or self.candidate_artifacts or self.superseded_artifact_ids:
            raise ValueError(f"{status} execution must not claim a candidate revision, artifacts or superseded IDs")
        if self.status in (ExecutionStatus.FAILED, ExecutionStatus.UNCERTAIN) and self.issue is None:
            raise ValueError(f"{status} execution requires an issue")

    @property
    def candidate_artifact_ids(self) -> frozenset[ArtifactId]:
        return frozenset(artifact.artifact_id for artifact in self.candidate_artifacts)


def validate_receipt_against_checkpoint(receipt: ExecutionReceipt, before: ArtifactCheckpoint) -> None:
    """Check that a receipt applies to the before state it claims to start from.

    Requires matching project and before revision, superseded IDs that are members of the
    before state, and candidate IDs disjoint from every before-state artifact ID (no reuse).
    """
    if receipt.project_id != before.project_id:
        raise ValueError(f"execution project {receipt.project_id} does not match checkpoint {before.project_id}")
    if receipt.before_revision != before.revision:
        raise ValueError(
            f"execution before revision {receipt.before_revision} does not match checkpoint revision {before.revision}"
        )
    unknown = sorted(str(a) for a in set(receipt.superseded_artifact_ids) - before.artifact_ids)
    if unknown:
        raise ValueError(f"superseded artifacts are not in the before checkpoint: {', '.join(unknown)}")
    reused = sorted(str(a) for a in receipt.candidate_artifact_ids & before.artifact_ids)
    if reused:
        raise ValueError(f"candidate artifact IDs reuse before-checkpoint IDs: {', '.join(reused)}")


def derive_candidate_checkpoint(
    previous: ArtifactCheckpoint, receipt: ExecutionReceipt, checkpoint_id: CheckpointId
) -> ArtifactCheckpoint:
    """Build the candidate state's membership: retained previous artifacts, then the new candidates.

    Retained artifacts are carried over unchanged (identity, hash, location and production
    revision), in their previous order, followed by the candidate artifacts in receipt order. The
    result represents the candidate revision. This constructs candidate membership only; it does
    not accept the correction.
    """
    require_instance(checkpoint_id, CheckpointId, "checkpoint_id")
    if receipt.status is not ExecutionStatus.CANDIDATE_READY:
        raise ValueError(f"candidate derivation requires a CANDIDATE_READY execution, got {receipt.status.name}")
    validate_receipt_against_checkpoint(receipt, previous)
    if receipt.candidate_revision is None:  # unreachable: CANDIDATE_READY receipts always carry one
        raise ValueError("candidate derivation requires a candidate revision")
    superseded = set(receipt.superseded_artifact_ids)
    retained = tuple(artifact for artifact in previous.artifacts if artifact.artifact_id not in superseded)
    return ArtifactCheckpoint(
        checkpoint_id, previous.project_id, receipt.candidate_revision, retained + receipt.candidate_artifacts
    )
