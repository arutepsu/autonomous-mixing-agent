"""Structural check of an analysis response against its request."""

from autonomous_mixing.application.observation.contracts import AnalysisRequest, AnalysisResponse
from autonomous_mixing.domain.observation import validate_observation_sources
from autonomous_mixing.domain.project import AnalysisScope
from autonomous_mixing.domain.shared import VersionRef, require_instance


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
