"""Application contracts and policies, organized into responsibility-owned components.

``shared`` (typed port results), ``observation`` and ``decision`` (port request/response records,
checks and ports; ADR-016), ``admission`` (explicit gain-action admission; ADR-018) and ``execution``
(execution requests, processing plans and outcomes, metadata preflight and the processor port;
ADR-020, ADR-021). This root module is a compatibility facade that re-exports the same objects from
those component interfaces; new code imports the components directly.

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
from autonomous_mixing.application.decision import DecisionRequest, DecisionResponse, validate_decision_response
from autonomous_mixing.application.execution import (
    ArtifactProcessingEvidence,
    CandidateIdentity,
    ExecutionRequest,
    ExecutionWorkspace,
    MetadataReady,
    PreflightCode,
    PreflightRejected,
    PreflightResult,
    ProcessedCandidate,
    ProcessingFailure,
    ProcessingOutcome,
    ProcessingPlan,
    StemBinding,
    preflight_execution,
    validate_processed_candidate,
)
from autonomous_mixing.application.observation import AnalysisRequest, AnalysisResponse, validate_analysis_response
from autonomous_mixing.application.shared import PortFailure, PortFailureCode, PortResult, Success

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
