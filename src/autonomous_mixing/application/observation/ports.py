"""Port for obtaining observations of a project state."""

from typing import Protocol

from autonomous_mixing.application.observation.contracts import AnalysisRequest, AnalysisResponse
from autonomous_mixing.application.shared import PortResult


class AudioAnalyzer(Protocol):
    """Analyzes artifacts under a versioned specification into typed observations.

    Implementations return expected failures as ``PortFailure``; callers validate successful
    responses with ``validate_analysis_response``.
    """

    def analyze(self, request: AnalysisRequest) -> PortResult[AnalysisResponse]: ...
