"""In-memory audio processing kernels for bounded offline gain and full-mix processing."""

from .dsp import apply_absolute_gain, sum_stems

__all__ = ["apply_absolute_gain", "sum_stems"]
