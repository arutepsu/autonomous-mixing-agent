"""Versioned analysis and render specifications (configuration data only)."""

from dataclasses import dataclass

from autonomous_mixing.domain.shared import (
    VersionRef,
    require_count,
    require_finite_result,
    require_instance,
    require_tuple_of,
)


@dataclass(frozen=True)
class AnalysisSpec:
    ref: VersionRef
    metric_ids: tuple[VersionRef, ...]

    def __post_init__(self) -> None:
        require_instance(self.ref, VersionRef, "AnalysisSpec.ref")
        require_tuple_of(self.metric_ids, VersionRef, "AnalysisSpec.metric_ids", nonempty=True, distinct=True)


@dataclass(frozen=True)
class RenderSpec:
    """Render configuration data; not a renderer."""

    ref: VersionRef
    sample_rate_hz: int
    channel_count: int

    def __post_init__(self) -> None:
        require_instance(self.ref, VersionRef, "RenderSpec.ref")
        require_count(self.sample_rate_hz, "RenderSpec.sample_rate_hz", minimum=1)
        if require_count(self.channel_count, "RenderSpec.channel_count", minimum=1) > 2:
            raise ValueError(f"RenderSpec.channel_count must be 1 or 2, got {self.channel_count}")
        require_finite_result(lambda: self.nyquist_hz, "RenderSpec Nyquist frequency")

    @property
    def nyquist_hz(self) -> float:
        return self.sample_rate_hz / 2
