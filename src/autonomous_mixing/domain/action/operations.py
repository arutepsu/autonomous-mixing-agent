"""Typed operations an action may propose. Proposal vocabulary only; no bounds are implied."""

from dataclasses import dataclass

from autonomous_mixing.domain.shared import (
    TrackId,
    require_finite,
    require_instance,
)


@dataclass(frozen=True)
class SetTrackGain:
    """Set a track's gain to an absolute value in dB (not a relative change). No bounds are implied."""

    track_id: TrackId
    value_db: float

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "SetTrackGain.track_id")
        require_finite(self.value_db, "SetTrackGain.value_db")
