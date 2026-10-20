"""Fixed run configuration embedded as immutable values, with structural snapshot checks."""

from dataclasses import dataclass

from autonomous_mixing.domain.context import MusicalContext
from autonomous_mixing.domain.decision import ControllerIdentity
from autonomous_mixing.domain.observation import AnalysisSpec, RenderSpec
from autonomous_mixing.domain.project import AnalysisScope, ProjectSnapshot
from autonomous_mixing.domain.run.budgets import BudgetLimits
from autonomous_mixing.domain.shared import (
    require_instance,
)
from autonomous_mixing.domain.validation import ValidationCriteria


@dataclass(frozen=True)
class RunConfiguration:
    """Fixed run configuration, embedded as immutable values rather than a reference to a mutable file."""

    scope: AnalysisScope
    analysis_spec: AnalysisSpec
    render_spec: RenderSpec
    context: MusicalContext
    criteria: ValidationCriteria
    controller: ControllerIdentity
    budget_limits: BudgetLimits

    def __post_init__(self) -> None:
        require_instance(self.scope, AnalysisScope, "RunConfiguration.scope")
        require_instance(self.analysis_spec, AnalysisSpec, "RunConfiguration.analysis_spec")
        require_instance(self.render_spec, RenderSpec, "RunConfiguration.render_spec")
        require_instance(self.context, MusicalContext, "RunConfiguration.context")
        require_instance(self.criteria, ValidationCriteria, "RunConfiguration.criteria")
        require_instance(self.controller, ControllerIdentity, "RunConfiguration.controller")
        require_instance(self.budget_limits, BudgetLimits, "RunConfiguration.budget_limits")

    def validate_against(self, snapshot: ProjectSnapshot) -> None:
        """Check structural references and scope containment.

        Condition scopes may be subsets of the run scope. This does not check scientific validity,
        audio alignment, threshold calibration or metric/unit compatibility.
        """
        self.scope.validate_against(snapshot)
        self.context.validate_against(snapshot)
        run_tracks = set(self.scope.track_ids)
        run_time = self.scope.time_range
        run_band = self.scope.frequency_range
        nyquist_hz = self.render_spec.nyquist_hz
        if run_band is not None and run_band.high_hz > nyquist_hz:
            raise ValueError(f"run scope frequency {run_band.high_hz} Hz exceeds render Nyquist {nyquist_hz} Hz")
        criteria = self.criteria
        for condition in (*criteria.targets, *criteria.improvements, *criteria.guards):
            name = condition.condition_id
            selector = condition.selector
            selector.scope.validate_against(snapshot)
            outside = sorted(str(t) for t in set(selector.scope.track_ids) - run_tracks)
            if outside:
                raise ValueError(f"condition {name} uses tracks outside the run scope: {', '.join(outside)}")
            time = selector.scope.time_range
            if time.start_seconds < run_time.start_seconds or time.end_seconds > run_time.end_seconds:
                raise ValueError(f"condition {name} time range lies outside the run scope")
            band = selector.scope.frequency_range
            if run_band is not None:
                if band is None:
                    raise ValueError(f"condition {name} needs an explicit frequency range within the run scope")
                if band.low_hz < run_band.low_hz or band.high_hz > run_band.high_hz:
                    raise ValueError(f"condition {name} frequency range lies outside the run scope")
            if band is not None and band.high_hz > nyquist_hz:
                raise ValueError(f"condition {name} frequency {band.high_hz} Hz exceeds render Nyquist {nyquist_hz} Hz")
            if selector.metric not in self.analysis_spec.metric_ids:
                raise ValueError(
                    f"condition {name} metric {selector.metric.name}@{selector.metric.version} "
                    "is not listed in the analysis spec"
                )
