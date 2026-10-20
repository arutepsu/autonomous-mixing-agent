"""Run component: configuration, budgets, lifecycle records and correction attempts.

Records only: no state machine, budget enforcement or coordinator.
"""

from autonomous_mixing.domain.run.attempt import AttemptDisposition, CorrectionAttempt
from autonomous_mixing.domain.run.budgets import BudgetLimits, BudgetUsage
from autonomous_mixing.domain.run.configuration import RunConfiguration
from autonomous_mixing.domain.run.references import validate_attempt_references
from autonomous_mixing.domain.run.run import FinalProjectState, Run, RunOutcome, RunState

__all__ = [
    "RunConfiguration",
    "BudgetLimits",
    "BudgetUsage",
    "RunState",
    "RunOutcome",
    "FinalProjectState",
    "Run",
    "AttemptDisposition",
    "CorrectionAttempt",
    "validate_attempt_references",
]
