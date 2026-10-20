"""Rollback receipts: restoration of a checkpoint's accepted artifact references.

Rollback restores previous accepted references rather than applying an inverse transformation.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.project import (
    ArtifactCheckpoint,
)
from autonomous_mixing.domain.shared import (
    ArtifactId,
    CheckpointId,
    ExecutionId,
    require_instance,
    require_text,
    require_tuple_of,
)


class RollbackStatus(Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class RollbackReceipt:
    """Result of restoring the accepted references of a checkpoint after an execution."""

    execution_id: ExecutionId
    checkpoint_id: CheckpointId
    status: RollbackStatus
    restored_artifact_ids: tuple[ArtifactId, ...]
    explanation: str

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "RollbackReceipt.execution_id")
        require_instance(self.checkpoint_id, CheckpointId, "RollbackReceipt.checkpoint_id")
        require_instance(self.status, RollbackStatus, "RollbackReceipt.status")
        require_tuple_of(
            self.restored_artifact_ids,
            ArtifactId,
            "RollbackReceipt.restored_artifact_ids",
            nonempty=False,
            distinct=True,
        )
        require_text(self.explanation, "RollbackReceipt.explanation")
        if self.status is RollbackStatus.VERIFIED and not self.restored_artifact_ids:
            raise ValueError("VERIFIED rollback requires restored artifact IDs")
        if self.status is not RollbackStatus.VERIFIED and self.restored_artifact_ids:
            raise ValueError(f"{self.status.name} rollback must not claim restored artifact IDs")


def validate_rollback_references(receipt: RollbackReceipt, checkpoint: ArtifactCheckpoint) -> None:
    """Check reference consistency only.

    Matching IDs are not proof of exact audio restoration: an adapter must verify artifact
    integrity and the current accepted-reference state before issuing VERIFIED.
    """
    if receipt.checkpoint_id != checkpoint.checkpoint_id:
        raise ValueError(f"rollback refers to checkpoint {receipt.checkpoint_id}, not {checkpoint.checkpoint_id}")
    if receipt.status is RollbackStatus.VERIFIED:
        restored = set(receipt.restored_artifact_ids)
        missing = sorted(str(a) for a in checkpoint.artifact_ids - restored)
        extra = sorted(str(a) for a in restored - checkpoint.artifact_ids)
        if missing or extra:
            raise ValueError(f"verified rollback does not match the checkpoint (missing: {missing}, extra: {extra})")
