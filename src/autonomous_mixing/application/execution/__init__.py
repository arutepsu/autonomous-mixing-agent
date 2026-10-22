"""Execution component: execution identities and requests, processing plans and outcomes, candidate
validation, metadata preflight and the processor port (ADR-020, ADR-021).

Metadata only: nothing here resolves locations, allocates workspaces, writes files or orchestrates.
"""

from autonomous_mixing.application.execution.identity import CandidateIdentity, ExecutionWorkspace
from autonomous_mixing.application.execution.ports import AudioProcessor
from autonomous_mixing.application.execution.preflight import (
    MetadataReady,
    PreflightCode,
    PreflightRejected,
    PreflightResult,
    preflight_execution,
)
from autonomous_mixing.application.execution.processing import (
    ArtifactProcessingEvidence,
    ProcessedCandidate,
    ProcessingFailure,
    ProcessingOutcome,
    ProcessingPlan,
)
from autonomous_mixing.application.execution.requests import ExecutionRequest, StemBinding
from autonomous_mixing.application.execution.validation import validate_processed_candidate

__all__ = [
    "ExecutionWorkspace",
    "CandidateIdentity",
    "StemBinding",
    "ExecutionRequest",
    "ProcessingPlan",
    "ArtifactProcessingEvidence",
    "ProcessedCandidate",
    "ProcessingFailure",
    "ProcessingOutcome",
    "validate_processed_candidate",
    "PreflightCode",
    "PreflightRejected",
    "MetadataReady",
    "PreflightResult",
    "preflight_execution",
    "AudioProcessor",
]
