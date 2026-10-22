"""Shared application component: generic typed port results only.

Holds no processing plans, policy, provider objects, filesystem configuration or feature-specific helpers.
"""

from autonomous_mixing.application.shared.results import PortFailure, PortFailureCode, PortResult, Success

__all__ = ["Success", "PortFailureCode", "PortFailure", "PortResult"]
