"""Compatibility shim: re-exports the execution request and processing records from
``autonomous_mixing.application.execution``.

Deprecated import location kept for existing callers; new code imports from
``autonomous_mixing.application.execution``. Contains no definitions of its own.
"""

from autonomous_mixing.application.execution import (
    ArtifactProcessingEvidence,
    CandidateIdentity,
    ExecutionRequest,
    ExecutionWorkspace,
    ProcessedCandidate,
    ProcessingFailure,
    ProcessingOutcome,
    ProcessingPlan,
    StemBinding,
    validate_processed_candidate,
)

__all__ = [
    "StemBinding",
    "ExecutionWorkspace",
    "CandidateIdentity",
    "ExecutionRequest",
    "ProcessingPlan",
    "ArtifactProcessingEvidence",
    "ProcessedCandidate",
    "ProcessingFailure",
    "ProcessingOutcome",
    "validate_processed_candidate",
]
