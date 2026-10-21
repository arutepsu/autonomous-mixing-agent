"""Request/response records for the observation and decision ports, with structural checks.

Requests carry one composite ``ProjectState`` (ADR-019): its snapshot, gain processing settings and
audio membership are consistent by construction, so callers cannot pair a snapshot with audio from
another state. Audio members keep their own production revisions (ADR-011, ADR-015).

These contracts check structure, provenance and completeness only: not numeric correctness,
perceptual validity, evidence sufficiency, budgets or execution permissions. The decision
request is not the complete future controller input: problem candidates (FR-05, D11),
action capabilities and permitted actions (D5), attempt history and raw provider responses are
deferred contracts. Hidden evaluation data never belongs in these records (SR-10).
"""

from dataclasses import dataclass

from autonomous_mixing.domain.context import MusicalContext
from autonomous_mixing.domain.decision import ControllerIdentity, Decision, validate_decision_references
from autonomous_mixing.domain.observation import AnalysisSpec, Observation, validate_observation_sources
from autonomous_mixing.domain.project import AnalysisScope, ProjectState
from autonomous_mixing.domain.run import BudgetLimits, BudgetUsage
from autonomous_mixing.domain.shared import VersionRef, require_instance, require_tuple_of


def _require_unique_observations(observations: tuple[Observation, ...], field: str) -> None:
    require_tuple_of(observations, Observation, field, nonempty=False, distinct=False)
    ids = [observation.observation_id for observation in observations]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field} must have unique observation IDs")


def _require_scope_within(inner: AnalysisScope, outer: AnalysisScope, label: str) -> None:
    outside = sorted(str(t) for t in set(inner.track_ids) - set(outer.track_ids))
    if outside:
        raise ValueError(f"{label} uses tracks outside the requested scope: {', '.join(outside)}")
    if (
        inner.time_range.start_seconds < outer.time_range.start_seconds
        or inner.time_range.end_seconds > outer.time_range.end_seconds
    ):
        raise ValueError(f"{label} time range lies outside the requested scope")
    if outer.frequency_range is not None:
        band = inner.frequency_range
        if band is None:
            raise ValueError(f"{label} needs an explicit frequency range within the requested scope")
        if band.low_hz < outer.frequency_range.low_hz or band.high_hz > outer.frequency_range.high_hz:
            raise ValueError(f"{label} frequency range lies outside the requested scope")


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


def validate_analysis_response(request: AnalysisRequest, response: AnalysisResponse) -> None:
    """Check provenance, specification, scope containment and metric completeness of a response."""
    require_instance(request, AnalysisRequest, "request")
    require_instance(response, AnalysisResponse, "response")
    requested = request.specification.metric_ids
    produced: set[VersionRef] = set()
    seen: set[tuple[VersionRef, AnalysisScope]] = set()
    for observation in response.observations:
        label = f"observation {observation.observation_id}"
        audio, snapshot = request.state.audio, request.state.snapshot
        validate_observation_sources(observation, audio.artifacts, audio, snapshot)
        if observation.analysis_spec != request.specification.ref:
            raise ValueError(f"{label} uses analysis spec {observation.analysis_spec}, not the requested one")
        if observation.metric not in requested:
            raise ValueError(
                f"{label} reports unrequested metric {observation.metric.name}@{observation.metric.version}"
            )
        _require_scope_within(observation.scope, request.scope, label)
        key = (observation.metric, observation.scope)
        if key in seen:
            raise ValueError(f"{label} duplicates another observation of the same metric and scope")
        seen.add(key)
        produced.add(observation.metric)
    missing = [f"{m.name}@{m.version}" for m in requested if m not in produced]
    if missing:
        raise ValueError(f"no observation for requested metrics: {', '.join(missing)}")


@dataclass(frozen=True)
class DecisionRequest:
    """Runtime-visible inputs for one decision.

    Usage may exceed limits (the record describes, it does not enforce). Artifact locations are
    ordinary runtime source references; this record alone does not sandbox a provider.
    """

    state: ProjectState
    context: MusicalContext
    controller: ControllerIdentity
    observations: tuple[Observation, ...]
    usage: BudgetUsage
    limits: BudgetLimits

    def __post_init__(self) -> None:
        require_instance(self.state, ProjectState, "DecisionRequest.state")
        require_instance(self.context, MusicalContext, "DecisionRequest.context")
        require_instance(self.controller, ControllerIdentity, "DecisionRequest.controller")
        _require_unique_observations(self.observations, "DecisionRequest.observations")
        require_instance(self.usage, BudgetUsage, "DecisionRequest.usage")
        require_instance(self.limits, BudgetLimits, "DecisionRequest.limits")
        snapshot, audio = self.state.snapshot, self.state.audio
        self.context.validate_against(snapshot)
        for observation in self.observations:
            validate_observation_sources(observation, audio.artifacts, audio, snapshot)


@dataclass(frozen=True)
class DecisionResponse:
    decision: Decision

    def __post_init__(self) -> None:
        require_instance(self.decision, Decision, "DecisionResponse.decision")


def validate_decision_response(request: DecisionRequest, response: DecisionResponse) -> None:
    """Check a decision's structural references and controller identity against its request."""
    require_instance(request, DecisionRequest, "request")
    require_instance(response, DecisionResponse, "response")
    decision = response.decision
    validate_decision_references(decision, request.state.snapshot, request.context, request.observations)
    if decision.controller != request.controller:
        raise ValueError(
            f"decision controller {decision.controller.name}@{decision.controller.version} does not match "
            f"the requested controller {request.controller.name}@{request.controller.version}"
        )
