"""Compatibility shim: re-exports ``AudioProcessor`` from ``autonomous_mixing.application.execution``.

Deprecated import location kept for existing callers. Contains no definitions of its own.
"""

from autonomous_mixing.application.execution import AudioProcessor

__all__ = ["AudioProcessor"]
