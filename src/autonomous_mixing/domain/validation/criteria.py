"""Validation criteria: target, improvement and guard conditions over exact metric selectors.

These records describe conditions; they do not compute verdicts, compare thresholds or define
metrics. Units are explicit strings whose catalog compatibility is not established here.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.observation import MeasuredScalar
from autonomous_mixing.domain.project import AnalysisScope
from autonomous_mixing.domain.shared import (
    ConditionId,
    CriteriaId,
    VersionRef,
    require_instance,
    require_text,
    require_tuple_of,
)


@dataclass(frozen=True)
class MetricSelector:
    """Exact metric version and analysis scope; no implicit unit conversion or compatibility inference."""

    metric: VersionRef
    scope: AnalysisScope

    def __post_init__(self) -> None:
        require_instance(self.metric, VersionRef, "MetricSelector.metric")
        require_instance(self.scope, AnalysisScope, "MetricSelector.scope")


class ComparisonOperator(Enum):
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"


class ImprovementDirection(Enum):
    LOWER = "lower"
    HIGHER = "higher"


class BaselineReference(Enum):
    ATTEMPT = "attempt"
    INITIAL = "initial"


def _require_condition_fields(condition_id: ConditionId, selector: MetricSelector, owner: str) -> None:
    require_instance(condition_id, ConditionId, f"{owner}.condition_id")
    require_instance(selector, MetricSelector, f"{owner}.selector")


@dataclass(frozen=True)
class TargetCondition:
    condition_id: ConditionId
    selector: MetricSelector
    operator: ComparisonOperator
    threshold: MeasuredScalar

    def __post_init__(self) -> None:
        _require_condition_fields(self.condition_id, self.selector, "TargetCondition")
        require_instance(self.operator, ComparisonOperator, "TargetCondition.operator")
        require_instance(self.threshold, MeasuredScalar, "TargetCondition.threshold")


@dataclass(frozen=True)
class ImprovementCondition:
    """Minimum absolute change, in the metric's stated unit, relative to the pre-attempt state (not a percentage)."""

    condition_id: ConditionId
    selector: MetricSelector
    direction: ImprovementDirection
    minimum_delta: MeasuredScalar

    def __post_init__(self) -> None:
        _require_condition_fields(self.condition_id, self.selector, "ImprovementCondition")
        require_instance(self.direction, ImprovementDirection, "ImprovementCondition.direction")
        require_instance(self.minimum_delta, MeasuredScalar, "ImprovementCondition.minimum_delta")
        if self.minimum_delta.value <= 0:
            raise ValueError("ImprovementCondition.minimum_delta must be strictly positive")


@dataclass(frozen=True)
class AbsoluteGuard:
    condition_id: ConditionId
    selector: MetricSelector
    operator: ComparisonOperator
    threshold: MeasuredScalar

    def __post_init__(self) -> None:
        _require_condition_fields(self.condition_id, self.selector, "AbsoluteGuard")
        require_instance(self.operator, ComparisonOperator, "AbsoluteGuard.operator")
        require_instance(self.threshold, MeasuredScalar, "AbsoluteGuard.threshold")


@dataclass(frozen=True)
class DeltaGuard:
    """Bounds the magnitude of change from the named baseline."""

    condition_id: ConditionId
    selector: MetricSelector
    baseline: BaselineReference
    maximum_absolute_delta: MeasuredScalar

    def __post_init__(self) -> None:
        _require_condition_fields(self.condition_id, self.selector, "DeltaGuard")
        require_instance(self.baseline, BaselineReference, "DeltaGuard.baseline")
        require_instance(self.maximum_absolute_delta, MeasuredScalar, "DeltaGuard.maximum_absolute_delta")
        if self.maximum_absolute_delta.value < 0:
            raise ValueError("DeltaGuard.maximum_absolute_delta must be non-negative")


@dataclass(frozen=True)
class ValidationCriteria:
    """A versioned criteria definition. Guards may be empty here; configuration may require them later."""

    criteria_id: CriteriaId
    version: str
    targets: tuple[TargetCondition, ...]
    improvements: tuple[ImprovementCondition, ...]
    guards: tuple[AbsoluteGuard | DeltaGuard, ...]

    def __post_init__(self) -> None:
        require_instance(self.criteria_id, CriteriaId, "ValidationCriteria.criteria_id")
        require_text(self.version, "ValidationCriteria.version")
        require_tuple_of(self.targets, TargetCondition, "ValidationCriteria.targets", nonempty=True, distinct=False)
        require_tuple_of(
            self.improvements, ImprovementCondition, "ValidationCriteria.improvements", nonempty=True, distinct=False
        )
        if not isinstance(self.guards, tuple):
            raise ValueError(f"ValidationCriteria.guards must be a tuple, got {type(self.guards).__name__}")
        for guard in self.guards:
            require_instance(guard, (AbsoluteGuard, DeltaGuard), "ValidationCriteria.guards element")
        seen: set[ConditionId] = set()
        for condition in (*self.targets, *self.improvements, *self.guards):
            if condition.condition_id in seen:
                raise ValueError(f"duplicate condition ID in criteria: {condition.condition_id}")
            seen.add(condition.condition_id)
