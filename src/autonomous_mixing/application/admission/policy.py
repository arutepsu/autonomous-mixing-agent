"""Configured gain-admission policy: per-track absolute gain permissions for one project."""

from dataclasses import dataclass

from autonomous_mixing.domain.shared import (
    ProjectId,
    TrackId,
    VersionRef,
    require_finite,
    require_instance,
    require_tuple_of,
)


@dataclass(frozen=True)
class TrackGainPermission:
    """Configured absolute gain range for one track, in dB, inclusive at both ends.

    No default or scientifically motivated limits are implied; equal bounds permit one exact setting.
    """

    track_id: TrackId
    minimum_db: float
    maximum_db: float

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "TrackGainPermission.track_id")
        minimum = require_finite(self.minimum_db, "TrackGainPermission.minimum_db")
        maximum = require_finite(self.maximum_db, "TrackGainPermission.maximum_db")
        if minimum > maximum:
            raise ValueError(f"TrackGainPermission.minimum_db {minimum} exceeds maximum_db {maximum}")


@dataclass(frozen=True)
class ActionAdmissionPolicy:
    """Versioned admission configuration for one project. Empty permissions deny every gain action."""

    reference: VersionRef
    project_id: ProjectId
    gain_permissions: tuple[TrackGainPermission, ...]

    def __post_init__(self) -> None:
        require_instance(self.reference, VersionRef, "ActionAdmissionPolicy.reference")
        require_instance(self.project_id, ProjectId, "ActionAdmissionPolicy.project_id")
        require_tuple_of(
            self.gain_permissions,
            TrackGainPermission,
            "ActionAdmissionPolicy.gain_permissions",
            nonempty=False,
            distinct=False,
        )
        tracks = [permission.track_id for permission in self.gain_permissions]
        if len(set(tracks)) != len(tracks):
            raise ValueError("ActionAdmissionPolicy.gain_permissions must have at most one permission per track")
