"""Rollback receipts: exact restoration of a saved complete project state.

Rollback selects the saved before state (snapshot, gain settings and audio membership together)
rather than applying an inverse transformation. Failed or uncertain restoration cannot claim a
restored state.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.project import ProjectState
from autonomous_mixing.domain.shared import (
    CheckpointId,
    ExecutionId,
    require_instance,
    require_text,
)


class RollbackStatus(Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class RollbackReceipt:
    """Result of restoring the saved before state after an execution.

    ``restored_state`` is required for VERIFIED and forbidden otherwise. It records restoration of the
    saved state, including its original snapshot timestamp, not a newly captured snapshot.
    """

    execution_id: ExecutionId
    checkpoint_id: CheckpointId
    status: RollbackStatus
    restored_state: ProjectState | None
    explanation: str

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "RollbackReceipt.execution_id")
        require_instance(self.checkpoint_id, CheckpointId, "RollbackReceipt.checkpoint_id")
        require_instance(self.status, RollbackStatus, "RollbackReceipt.status")
        if self.restored_state is not None:
            require_instance(self.restored_state, ProjectState, "RollbackReceipt.restored_state")
        require_text(self.explanation, "RollbackReceipt.explanation")
        if self.status is RollbackStatus.VERIFIED and self.restored_state is None:
            raise ValueError("VERIFIED rollback requires the restored complete state")
        if self.status is not RollbackStatus.VERIFIED and self.restored_state is not None:
            raise ValueError(f"{self.status.name} rollback must not claim a restored state")


def validate_rollback_references(receipt: RollbackReceipt, before_state: ProjectState) -> None:
    """Check checkpoint identity and, for VERIFIED, exact equality with the saved before state.

    Equality covers settings, audio membership and snapshot together, so audio-only or settings-only
    restoration cannot be verified. Matching metadata is a recorded claim, not external proof: an
    adapter must verify files and the current accepted-reference state before issuing VERIFIED.
    """
    require_instance(receipt, RollbackReceipt, "receipt")
    require_instance(before_state, ProjectState, "before_state")
    if receipt.checkpoint_id != before_state.audio.checkpoint_id:
        raise ValueError(
            f"rollback refers to checkpoint {receipt.checkpoint_id}, not {before_state.audio.checkpoint_id}"
        )
    if receipt.status is RollbackStatus.VERIFIED and receipt.restored_state != before_state:
        restored = receipt.restored_state
        differing = [
            part
            for part in ("snapshot", "processing", "audio")
            if restored is None or getattr(restored, part) != getattr(before_state, part)
        ]
        raise ValueError(
            f"verified rollback does not restore the saved before state exactly (differs in: {', '.join(differing)})"
        )
