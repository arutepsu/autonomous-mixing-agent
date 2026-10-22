"""In-memory audio processing kernels and read-only WAV artifact verification for offline processing."""

from .dsp import apply_absolute_gain, sum_stems
from .verification import ArtifactVerificationError, VerificationFailureCode, VerifiedAudio, verify_wav_artifact

__all__ = [
    "ArtifactVerificationError",
    "VerificationFailureCode",
    "VerifiedAudio",
    "apply_absolute_gain",
    "sum_stems",
    "verify_wav_artifact",
]
