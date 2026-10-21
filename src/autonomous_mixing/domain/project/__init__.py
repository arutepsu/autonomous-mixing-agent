"""Project component: tracks, snapshots, analysis scopes, artifact metadata, state checkpoints,
gain processing state, composite project state,
full-mix recipes and processing specifications.

Records hold metadata only; no file access, audio loading or alignment inference happens here.
"""

from autonomous_mixing.domain.project.artifacts import ArtifactKind, AudioArtifact
from autonomous_mixing.domain.project.checkpoint import ArtifactCheckpoint
from autonomous_mixing.domain.project.mix import MixRecipe, SummingPolicy
from autonomous_mixing.domain.project.processing import ProjectProcessingState, TrackGainState
from autonomous_mixing.domain.project.processing_spec import (
    GainRule,
    LevelPolicy,
    NumericalPrecision,
    OutputContainer,
    ProcessingSpec,
    SampleEncoding,
    SummationOrder,
)
from autonomous_mixing.domain.project.scope import AnalysisScope, FrequencyRange, TimeRange
from autonomous_mixing.domain.project.snapshot import ProjectSnapshot
from autonomous_mixing.domain.project.state import ProjectState
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
    "TrackGainState",
    "ProjectProcessingState",
    "ProjectState",
    "SummingPolicy",
    "MixRecipe",
    "ProcessingSpec",
    "NumericalPrecision",
    "GainRule",
    "SummationOrder",
    "LevelPolicy",
    "OutputContainer",
    "SampleEncoding",
]
