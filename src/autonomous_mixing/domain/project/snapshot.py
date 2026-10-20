"""Observed project snapshot: identity, opaque revision, capture time and tracks."""

from dataclasses import dataclass
from datetime import datetime

from autonomous_mixing.domain.project.tracks import Track
from autonomous_mixing.domain.shared import (
    ProjectId,
    Revision,
    TrackId,
    require_instance,
    require_tuple_of,
    require_utc,
)


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
