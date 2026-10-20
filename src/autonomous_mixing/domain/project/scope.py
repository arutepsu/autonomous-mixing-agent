"""Analysis scope: tracks, project time range and optional frequency band."""

from dataclasses import dataclass

from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.shared import (
    TrackId,
    require_finite,
    require_instance,
    require_tuple_of,
)


@dataclass(frozen=True)
class TimeRange:
    """Project time in seconds, start-inclusive and end-exclusive, with positive extent."""

    start_seconds: float
    end_seconds: float

    def __post_init__(self) -> None:
        start = require_finite(self.start_seconds, "TimeRange.start_seconds")
        end = require_finite(self.end_seconds, "TimeRange.end_seconds")
        if start < 0:
            raise ValueError(f"TimeRange.start_seconds must be >= 0, got {start}")
        if end <= start:
            raise ValueError(f"TimeRange must have positive extent, got [{start}, {end})")


@dataclass(frozen=True)
class FrequencyRange:
    """Frequency band in Hz with positive extent; Nyquist is checked against artifact metadata elsewhere."""

    low_hz: float
    high_hz: float

    def __post_init__(self) -> None:
        low = require_finite(self.low_hz, "FrequencyRange.low_hz")
        high = require_finite(self.high_hz, "FrequencyRange.high_hz")
        if low < 0:
            raise ValueError(f"FrequencyRange.low_hz must be >= 0, got {low}")
        if high <= low:
            raise ValueError(f"FrequencyRange must have positive extent, got [{low}, {high}]")


@dataclass(frozen=True)
class AnalysisScope:
    track_ids: tuple[TrackId, ...]
    time_range: TimeRange
    frequency_range: FrequencyRange | None = None

    def __post_init__(self) -> None:
        require_tuple_of(self.track_ids, TrackId, "AnalysisScope.track_ids", nonempty=True, distinct=True)
        require_instance(self.time_range, TimeRange, "AnalysisScope.time_range")
        if self.frequency_range is not None:
            require_instance(self.frequency_range, FrequencyRange, "AnalysisScope.frequency_range")

    def validate_against(self, snapshot: ProjectSnapshot) -> None:
        snapshot.require_known_tracks(self.track_ids, "AnalysisScope.track_ids")
