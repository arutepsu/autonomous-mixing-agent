"""Compatibility shim: re-exports ``AudioAnalyzer`` from ``autonomous_mixing.application.observation``.

Deprecated import location kept for existing callers. Contains no definitions of its own.
"""

from autonomous_mixing.application.observation import AudioAnalyzer

__all__ = ["AudioAnalyzer"]
