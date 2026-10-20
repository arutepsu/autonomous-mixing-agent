"""Project snapshot, analysis scope and audio artifact metadata.

Records hold metadata only; no file access, audio loading or alignment inference happens here.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from autonomous_mixing.domain.values import (
    ArtifactId,
    ProjectId,
    Revision,
    TrackId,
    VersionRef,
    require_count,
    require_finite,
    require_finite_result,
    require_instance,
    require_text,
    require_tuple_of,
    require_utc,
)

_SHA256_HEX = re.compile(r"[0-9a-f]{64}")


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
class Track:
    """A track with stable identity. Musical roles are declared in MusicalContext, never derived from the name."""

    track_id: TrackId
    name: str

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "Track.track_id")
        require_text(self.name, "Track.name")


@dataclass(frozen=True)
class ProjectSnapshot:
    project_id: ProjectId
    revision: Revision
    captured_at: datetime
    tracks: tuple[Track, ...]

    def __post_init__(self) -> None:
        require_instance(self.project_id, ProjectId, "ProjectSnapshot.project_id")
        require_instance(self.revision, Revision, "ProjectSnapshot.revision")
        require_utc(self.captured_at, "ProjectSnapshot.captured_at")
        require_tuple_of(self.tracks, Track, "ProjectSnapshot.tracks", nonempty=True, distinct=False)
        ids = [track.track_id for track in self.tracks]
        if len(set(ids)) != len(ids):
            raise ValueError("ProjectSnapshot.tracks must have unique track IDs")

    @property
    def track_ids(self) -> frozenset[TrackId]:
        return frozenset(track.track_id for track in self.tracks)

    def require_known_tracks(self, track_ids: tuple[TrackId, ...] | frozenset[TrackId], field: str) -> None:
        unknown = sorted(str(t) for t in set(track_ids) - self.track_ids)
        if unknown:
            raise ValueError(f"{field} references tracks not in project {self.project_id}: {', '.join(unknown)}")


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


class ArtifactKind(Enum):
    STEM = "stem"
    GROUP = "group"
    MIX = "mix"


@dataclass(frozen=True)
class AudioArtifact:
    """Metadata of rendered or supplied audio. The hash establishes file identity, not perceptual equivalence.

    ``revision`` is the production revision: the project state the artifact was produced from.
    It is provenance and is never retagged; membership of a later state is recorded by an
    ``ArtifactCheckpoint``. Derived timeline end and Nyquist values must be finite floats.
    """

    artifact_id: ArtifactId
    project_id: ProjectId
    revision: Revision
    source_track_ids: tuple[TrackId, ...]
    kind: ArtifactKind
    location: str
    timeline_start_seconds: float
    sample_rate_hz: int
    channel_count: int
    frame_count: int
    content_hash: str
    render_spec: VersionRef

    def __post_init__(self) -> None:
        require_instance(self.artifact_id, ArtifactId, "AudioArtifact.artifact_id")
        require_instance(self.project_id, ProjectId, "AudioArtifact.project_id")
        require_instance(self.revision, Revision, "AudioArtifact.revision")
        require_tuple_of(self.source_track_ids, TrackId, "AudioArtifact.source_track_ids", nonempty=True, distinct=True)
        require_instance(self.kind, ArtifactKind, "AudioArtifact.kind")
        require_text(self.location, "AudioArtifact.location")
        if require_finite(self.timeline_start_seconds, "AudioArtifact.timeline_start_seconds") < 0:
            raise ValueError("AudioArtifact.timeline_start_seconds must be >= 0")
        require_count(self.sample_rate_hz, "AudioArtifact.sample_rate_hz", minimum=1)
        if require_count(self.channel_count, "AudioArtifact.channel_count", minimum=1) > 2:
            raise ValueError(f"AudioArtifact.channel_count must be 1 or 2, got {self.channel_count}")
        require_count(self.frame_count, "AudioArtifact.frame_count", minimum=0)
        if not isinstance(self.content_hash, str) or not _SHA256_HEX.fullmatch(self.content_hash):
            raise ValueError("AudioArtifact.content_hash must be a lowercase SHA-256 hex digest")
        require_instance(self.render_spec, VersionRef, "AudioArtifact.render_spec")
        require_finite_result(lambda: self.timeline_end_seconds, "AudioArtifact timeline end")
        require_finite_result(lambda: self.nyquist_hz, "AudioArtifact Nyquist frequency")

    @property
    def timeline_end_seconds(self) -> float:
        """End of the covered project time, derived from metadata only (no alignment verification)."""
        return self.timeline_start_seconds + self.frame_count / self.sample_rate_hz

    @property
    def nyquist_hz(self) -> float:
        return self.sample_rate_hz / 2
