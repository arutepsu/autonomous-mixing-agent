"""Compatibility shim: re-exports the typed port results from ``autonomous_mixing.application.shared``.

Deprecated import location kept for existing callers; new code imports from
``autonomous_mixing.application.shared``. Contains no definitions of its own.
"""

from autonomous_mixing.application.shared import PortFailure, PortFailureCode, PortResult, Success

__all__ = ["Success", "PortFailureCode", "PortFailure", "PortResult"]
