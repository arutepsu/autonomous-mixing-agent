"""Tracks with stable identity; musical roles live in the context component."""

from dataclasses import dataclass

from autonomous_mixing.domain.shared import (
    TrackId,
    require_instance,
    require_text,
)


@dataclass(frozen=True)
class Track:
    """A track with stable identity. Musical roles are declared in MusicalContext, never derived from the name."""

    track_id: TrackId
    name: str

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "Track.track_id")
        require_text(self.name, "Track.name")
