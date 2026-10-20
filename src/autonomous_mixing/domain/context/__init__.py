"""Context component: explicitly supplied musical context with provenance.

Unknown information is represented by absence. Nothing here derives roles or intent from
track names, genres or audio.
"""

from autonomous_mixing.domain.context.assertions import AssertionSource, ContextPreference, TrackRole
from autonomous_mixing.domain.context.musical_context import MusicalContext

__all__ = [
    "AssertionSource",
    "TrackRole",
    "ContextPreference",
    "MusicalContext",
]
