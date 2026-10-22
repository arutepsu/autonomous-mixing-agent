"""Compatibility shim: re-exports the metadata preflight from ``autonomous_mixing.application.execution``.

Deprecated import location kept for existing callers; new code imports from
``autonomous_mixing.application.execution``. Contains no definitions of its own.
"""

from autonomous_mixing.application.execution import (
    MetadataReady,
    PreflightCode,
    PreflightRejected,
    PreflightResult,
    preflight_execution,
)

__all__ = ["PreflightCode", "PreflightRejected", "MetadataReady", "PreflightResult", "preflight_execution"]
