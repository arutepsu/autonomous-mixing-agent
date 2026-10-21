"""Application contracts and policies: typed port results, observation/decision request records
(ADR-016) and explicit gain-action admission (ADR-018).

Depends only on the standard library and ``autonomous_mixing.domain`` component interfaces; no
infrastructure, presentation, audio, provider or storage imports. No services or orchestration yet.
"""

from autonomous_mixing.application.admission import (
    ActionAdmissionPolicy,
    ActionAdmissionRequest,
    AdmissionRejectionCode,
    AdmissionResult,
    AdmittedAction,
    RejectedAction,
    TrackGainPermission,
    admit_action,
)
from autonomous_mixing.application.contracts import (
    AnalysisRequest,
    AnalysisResponse,
    DecisionRequest,
    DecisionResponse,
    validate_analysis_response,
    validate_decision_response,
)
from autonomous_mixing.application.execution_contracts import (
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
from autonomous_mixing.application.execution_preflight import (
    MetadataReady,
    PreflightCode,
    PreflightRejected,
    PreflightResult,
    preflight_execution,
)
from autonomous_mixing.application.results import PortFailure, PortFailureCode, PortResult, Success

__all__ = [
    "ActionAdmissionPolicy",
    "ActionAdmissionRequest",
    "AdmissionRejectionCode",
    "AdmissionResult",
    "AdmittedAction",
    "AnalysisRequest",
    "AnalysisResponse",
    "DecisionRequest",
    "DecisionResponse",
    "PortFailure",
    "PortFailureCode",
    "PortResult",
    "RejectedAction",
    "Success",
    "TrackGainPermission",
    "admit_action",
    "validate_analysis_response",
    "validate_decision_response",
    "CandidateIdentity",
    "ExecutionRequest",
    "ExecutionWorkspace",
    "StemBinding",
    "ProcessingPlan",
    "MetadataReady",
    "PreflightCode",
    "PreflightRejected",
    "PreflightResult",
    "preflight_execution",
    "ArtifactProcessingEvidence",
    "ProcessedCandidate",
    "ProcessingFailure",
    "ProcessingOutcome",
    "validate_processed_candidate",
]
