"""Request/response records for the observation port.

Requests carry one composite ``ProjectState`` (ADR-019): its snapshot, gain processing settings and
audio membership are consistent by construction, so callers cannot pair a snapshot with audio from
another state. Audio members keep their own production revisions (ADR-011, ADR-015).

These contracts check structure, provenance and completeness only: not numeric correctness,
perceptual validity or evidence sufficiency. Hidden evaluation data never belongs in these records (SR-10).
"""

from dataclasses import dataclass

from autonomous_mixing.domain.observation import AnalysisSpec, Observation
from autonomous_mixing.domain.project import AnalysisScope, ProjectState
from autonomous_mixing.domain.shared import require_instance, require_tuple_of


def _require_unique_observations(observations: tuple[Observation, ...], field: str) -> None:
    require_tuple_of(observations, Observation, field, nonempty=False, distinct=False)
    ids = [observation.observation_id for observation in observations]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field} must have unique observation IDs")


@dataclass(frozen=True)
class AnalysisRequest:
    """Request to analyze one project state.

    Audio members need not each cover the whole scope, since different artifacts may serve different
    metrics. Source coverage is checked per resulting observation.
    """

    state: ProjectState
    scope: AnalysisScope
    specification: AnalysisSpec

    def __post_init__(self) -> None:
        require_instance(self.state, ProjectState, "AnalysisRequest.state")
        require_instance(self.scope, AnalysisScope, "AnalysisRequest.scope")
        require_instance(self.specification, AnalysisSpec, "AnalysisRequest.specification")
        self.scope.validate_against(self.state.snapshot)


@dataclass(frozen=True)
class AnalysisResponse:
    """Observations produced for a request. Empty is structurally valid; completeness is request-relative."""

    observations: tuple[Observation, ...]

    def __post_init__(self) -> None:
        _require_unique_observations(self.observations, "AnalysisResponse.observations")
