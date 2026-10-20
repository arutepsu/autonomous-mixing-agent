"""Sourced context assertions: provenance, track roles and preferences."""

from dataclasses import dataclass
from datetime import datetime

from autonomous_mixing.domain.shared import (
    TrackId,
    require_instance,
    require_text,
    require_tuple_of,
    require_utc,
)


@dataclass(frozen=True)
class AssertionSource:
    """Who supplied a context assertion, and when."""

    source_id: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        require_text(self.source_id, "AssertionSource.source_id")
        require_utc(self.recorded_at, "AssertionSource.recorded_at")


@dataclass(frozen=True)
class TrackRole:
    track_id: TrackId
    role: str
    source: AssertionSource

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "TrackRole.track_id")
        require_text(self.role, "TrackRole.role")
        require_instance(self.source, AssertionSource, "TrackRole.source")


@dataclass(frozen=True)
class ContextPreference:
    """A declared preference; an empty ``track_ids`` tuple means it is not tied to specific tracks."""

    description: str
    track_ids: tuple[TrackId, ...]
    source: AssertionSource

    def __post_init__(self) -> None:
        require_text(self.description, "ContextPreference.description")
        require_tuple_of(self.track_ids, TrackId, "ContextPreference.track_ids", nonempty=False, distinct=True)
        require_instance(self.source, AssertionSource, "ContextPreference.source")
