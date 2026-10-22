"""Compatibility shim: re-exports ``DecisionController`` from ``autonomous_mixing.application.decision``.

Deprecated import location kept for existing callers. Contains no definitions of its own.
"""

from autonomous_mixing.application.decision import DecisionController

__all__ = ["DecisionController"]
