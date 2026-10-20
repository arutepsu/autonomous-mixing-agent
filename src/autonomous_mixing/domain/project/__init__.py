"""Project component: tracks, snapshots, analysis scopes, artifact metadata and state checkpoints.

Records hold metadata only; no file access, audio loading or alignment inference happens here.
"""

from autonomous_mixing.domain.project.artifacts import ArtifactKind, AudioArtifact
from autonomous_mixing.domain.project.checkpoint import ArtifactCheckpoint
from autonomous_mixing.domain.project.scope import AnalysisScope, FrequencyRange, TimeRange
from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.project.tracks import Track

__all__ = [
    "Track",
    "ProjectSnapshot",
    "AudioArtifact",
    "ArtifactKind",
    "ArtifactCheckpoint",
    "AnalysisScope",
    "TimeRange",
    "FrequencyRange",
]
