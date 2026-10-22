"""Admission component: explicit gain-action admission policy, its records and ``admit_action`` (ADR-018).

Replaces the former flat ``application/admission.py`` at the same dotted path. See
``autonomous_mixing.application.admission.admission`` for the limits of the check.
"""

from autonomous_mixing.application.admission.admission import admit_action
from autonomous_mixing.application.admission.contracts import (
    ActionAdmissionRequest,
    AdmissionRejectionCode,
    AdmissionResult,
    AdmittedAction,
    RejectedAction,
)
from autonomous_mixing.application.admission.policy import ActionAdmissionPolicy, TrackGainPermission

__all__ = [
    "TrackGainPermission",
    "ActionAdmissionPolicy",
    "ActionAdmissionRequest",
    "AdmissionRejectionCode",
    "AdmittedAction",
    "RejectedAction",
    "AdmissionResult",
    "admit_action",
]
