"""Run lifecycle state and terminal-outcome records.

``Run`` is an immutable record, not an executable state machine: legal transitions depend on
attempt and mutation-state contracts that are not defined yet.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from autonomous_mixing.domain.run.budgets import BudgetUsage
from autonomous_mixing.domain.run.configuration import RunConfiguration
from autonomous_mixing.domain.shared import (
    ProjectId,
    Revision,
    RunId,
    require_instance,
    require_text,
    require_utc,
)


class RunState(Enum):
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    DECIDING = "deciding"
    CHECKING_ACTION = "checking_action"
    PREPARING_EXECUTION = "preparing_execution"
    EXECUTING = "executing"
    RECONCILING = "reconciling"
    ANALYZING_RESULT = "analyzing_result"
    VALIDATING = "validating"
    RESTORING = "restoring"
    FINISHED = "finished"


class RunOutcome(Enum):
    SUCCEEDED = "succeeded"
    ABSTAINED = "abstained"
    LIMIT_REACHED = "limit_reached"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FinalProjectState(Enum):
    """Disposition of project outputs at the end of a run, reported separately from the run outcome."""

    UNCHANGED = "unchanged"
    ACCEPTED_EDITS_RETAINED = "accepted_edits_retained"
    RESTORED_TO_LAST_ACCEPTED = "restored_to_last_accepted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Run:
    """Immutable run record. FINISHED runs carry all terminal fields; active runs carry none."""

    run_id: RunId
    project_id: ProjectId
    configuration: RunConfiguration
    initial_revision: Revision
    created_at: datetime
    state: RunState
    usage: BudgetUsage
    outcome: RunOutcome | None
    final_project_state: FinalProjectState | None
    termination_reason: str | None

    def __post_init__(self) -> None:
        require_instance(self.run_id, RunId, "Run.run_id")
        require_instance(self.project_id, ProjectId, "Run.project_id")
        require_instance(self.configuration, RunConfiguration, "Run.configuration")
        require_instance(self.initial_revision, Revision, "Run.initial_revision")
        require_utc(self.created_at, "Run.created_at")
        require_instance(self.state, RunState, "Run.state")
        require_instance(self.usage, BudgetUsage, "Run.usage")

        if self.state is RunState.FINISHED:
            require_instance(self.outcome, RunOutcome, "Run.outcome")
            require_instance(self.final_project_state, FinalProjectState, "Run.final_project_state")
            require_text(self.termination_reason, "Run.termination_reason")
            if self.outcome is RunOutcome.SUCCEEDED and self.final_project_state is FinalProjectState.UNKNOWN:
                raise ValueError("SUCCEEDED run cannot have UNKNOWN final project state")
        elif (self.outcome, self.final_project_state, self.termination_reason) != (None, None, None):
            raise ValueError(f"run in state {self.state.name} must not have terminal fields")
