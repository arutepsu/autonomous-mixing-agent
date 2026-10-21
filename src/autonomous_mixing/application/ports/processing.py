"""Port for bounded offline gain/full-mix processing."""

from typing import Protocol

from autonomous_mixing.application.execution_contracts import ProcessingOutcome, ProcessingPlan


class AudioProcessor(Protocol):
    """Renders a plan's fixed target input at the requested gain and the full mix from current stems.

    Returns a ``ProcessedCandidate`` or a typed ``ProcessingFailure``; callers check candidates with
    ``validate_processed_candidate``. It must not choose actions, read hidden evaluation data, accept
    audio or change policy. No implementation exists in the application layer.
    """

    def process(self, plan: ProcessingPlan) -> ProcessingOutcome: ...
