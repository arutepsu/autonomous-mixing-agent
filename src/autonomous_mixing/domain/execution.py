"""Compatibility shim: re-exports the former ``execution`` module's objects from their owners.

``ArtifactCheckpoint`` is owned by ``autonomous_mixing.domain.project``; receipts, rollback and
candidate derivation by ``autonomous_mixing.domain.action``. Deprecated import location kept for
existing callers; contains no definitions of its own.
"""

from autonomous_mixing.domain.action import (
    ExecutionIssue,
    ExecutionReceipt,
    ExecutionStatus,
    RollbackReceipt,
    RollbackStatus,
    derive_candidate_checkpoint,
    validate_receipt_against_checkpoint,
    validate_rollback_references,
)
from autonomous_mixing.domain.project import ArtifactCheckpoint

__all__ = [
    "ArtifactCheckpoint",
    "ExecutionStatus",
    "ExecutionIssue",
    "ExecutionReceipt",
    "validate_receipt_against_checkpoint",
    "RollbackStatus",
    "RollbackReceipt",
    "validate_rollback_references",
    "derive_candidate_checkpoint",
]
