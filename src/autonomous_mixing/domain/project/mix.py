"""Versioned full-mix recipe: logical contributing tracks and an explicit summing policy.

A recipe names logical tracks, not artifacts, so it survives artifact replacement. It does not
claim equivalence to an original producer mix or infer baked-in routing or fader history.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.shared import TrackId, VersionRef, require_instance, require_tuple_of


class SummingPolicy(Enum):
    """Sample-wise addition of current stems, without automatic normalization, limiting or clipping."""

    SAMPLE_SUM = "sample_sum"


@dataclass(frozen=True)
class MixRecipe:
    """Ordered, unique logical contributors; summation order follows ``track_ids``. No defaults are implied."""

    reference: VersionRef
    track_ids: tuple[TrackId, ...]
    summing_policy: SummingPolicy

    def __post_init__(self) -> None:
        require_instance(self.reference, VersionRef, "MixRecipe.reference")
        require_tuple_of(self.track_ids, TrackId, "MixRecipe.track_ids", nonempty=True, distinct=True)
        require_instance(self.summing_policy, SummingPolicy, "MixRecipe.summing_policy")
