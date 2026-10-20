"""Validation criteria and validation result records.

These records describe conditions and recorded outcomes; they do not compute verdicts,
compare thresholds, define metrics or inspect audio. Units are explicit strings whose
compatibility with a future metric catalog is not established here.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.observation import MeasuredScalar
from autonomous_mixing.domain.project import AnalysisScope
from autonomous_mixing.domain.values import (
    ConditionId,
    CriteriaId,
    ObservationId,
    ValidationResultId,
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


class AssessmentMode(Enum):
    INITIAL = "initial"
    ATTEMPT = "attempt"


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"  # intentionally outside the assessment mode, not missing evidence


class ValidationVerdict(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class TargetStatus(Enum):
    SATISFIED = "satisfied"
    UNMET = "unmet"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CheckResult:
    condition_id: ConditionId
    status: CheckStatus
    explanation: str
    evidence_ids: tuple[ObservationId, ...]

    def __post_init__(self) -> None:
        require_instance(self.condition_id, ConditionId, "CheckResult.condition_id")
        require_instance(self.status, CheckStatus, "CheckResult.status")
        require_text(self.explanation, "CheckResult.explanation")
        require_tuple_of(self.evidence_ids, ObservationId, "CheckResult.evidence_ids", nonempty=False, distinct=True)
        if self.status in (CheckStatus.PASS, CheckStatus.FAIL) and not self.evidence_ids:
            raise ValueError(f"CheckResult {self.condition_id} with status {self.status.name} requires evidence")


@dataclass(frozen=True)
class ValidationResult:
    """A recorded validation outcome. The verdict is supplied, not computed here.

    Construction rejects only combinations that are contradictory without the criteria. Whether
    a FAIL check is consistent with ACCEPTED depends on its category (target, improvement or
    guard) and is checked by ``validate_validation_references``.
    """

    validation_result_id: ValidationResultId
    criteria_id: CriteriaId
    criteria_version: str
    mode: AssessmentMode
    checks: tuple[CheckResult, ...]
    verdict: ValidationVerdict
    target_status: TargetStatus

    def __post_init__(self) -> None:
        require_instance(self.validation_result_id, ValidationResultId, "ValidationResult.validation_result_id")
        require_instance(self.criteria_id, CriteriaId, "ValidationResult.criteria_id")
        require_text(self.criteria_version, "ValidationResult.criteria_version")
        require_instance(self.mode, AssessmentMode, "ValidationResult.mode")
        require_tuple_of(self.checks, CheckResult, "ValidationResult.checks", nonempty=True, distinct=False)
        ids = [check.condition_id for check in self.checks]
        if len(set(ids)) != len(ids):
            raise ValueError("ValidationResult.checks must have unique condition IDs")
        require_instance(self.verdict, ValidationVerdict, "ValidationResult.verdict")
        require_instance(self.target_status, TargetStatus, "ValidationResult.target_status")

        if self.verdict is ValidationVerdict.ACCEPTED:
            statuses = {check.status for check in self.checks}
            if self.target_status is TargetStatus.UNKNOWN:
                raise ValueError("ACCEPTED result cannot have UNKNOWN target status")
            if CheckStatus.UNAVAILABLE in statuses:
                raise ValueError("ACCEPTED result cannot contain UNAVAILABLE checks")
            if self.mode is AssessmentMode.INITIAL:
                if self.target_status is not TargetStatus.SATISFIED:
                    raise ValueError("ACCEPTED INITIAL assessment requires SATISFIED target status")
                # Every INITIAL check is a passing target/absolute guard or NOT_APPLICABLE, whatever its category.
                if CheckStatus.FAIL in statuses:
                    raise ValueError("ACCEPTED INITIAL assessment cannot contain FAIL checks")


def validate_validation_references(result: ValidationResult, criteria: ValidationCriteria) -> None:
    """Check that a result's checks are consistent with a criteria definition.

    Record consistency only: no improvement calculation, threshold comparison, audio inspection,
    observation lookup or provenance check.
    """
    if result.criteria_id != criteria.criteria_id or result.criteria_version != criteria.version:
        raise ValueError(
            f"result references criteria {result.criteria_id}@{result.criteria_version}, "
            f"supplied criteria is {criteria.criteria_id}@{criteria.version}"
        )

    by_id = {check.condition_id: check for check in result.checks}
    configured = {c.condition_id for c in (*criteria.targets, *criteria.improvements, *criteria.guards)}
    missing = sorted(str(c) for c in configured - by_id.keys())
    extra = sorted(str(c) for c in by_id.keys() - configured)
    if missing or extra:
        raise ValueError(f"checks do not match criteria (missing: {missing}, extra: {extra})")

    na = CheckStatus.NOT_APPLICABLE
    deferred = [c.condition_id for c in criteria.improvements] + [
        g.condition_id for g in criteria.guards if isinstance(g, DeltaGuard)
    ]
    immediate = [c.condition_id for c in criteria.targets] + [
        g.condition_id for g in criteria.guards if isinstance(g, AbsoluteGuard)
    ]
    if result.mode is AssessmentMode.INITIAL:
        for condition_id in deferred:
            if by_id[condition_id].status is not na:
                raise ValueError(f"INITIAL assessment requires {condition_id} to be NOT_APPLICABLE")
        for condition_id in immediate:
            if by_id[condition_id].status is na:
                raise ValueError(f"INITIAL assessment cannot mark {condition_id} NOT_APPLICABLE")
    else:
        for check in result.checks:
            if check.status is na:
                raise ValueError(f"ATTEMPT assessment cannot mark {check.condition_id} NOT_APPLICABLE")

    if result.verdict is ValidationVerdict.ACCEPTED:
        # Acceptance: every guard passes, and either targets are SATISFIED or, for an UNMET target
        # (intermediate improvement), every improvement condition passes.
        for guard in criteria.guards:
            if by_id[guard.condition_id].status is CheckStatus.FAIL:
                raise ValueError(f"ACCEPTED result has failing guard {guard.condition_id}")
        if result.target_status is TargetStatus.UNMET:
            for improvement in criteria.improvements:
                if by_id[improvement.condition_id].status is not CheckStatus.PASS:
                    raise ValueError(
                        f"ACCEPTED result with UNMET targets requires improvement {improvement.condition_id} to PASS"
                    )

    target_statuses = [by_id[t.condition_id].status for t in criteria.targets]
    has_fail = CheckStatus.FAIL in target_statuses
    has_unavailable = CheckStatus.UNAVAILABLE in target_statuses
    if result.target_status is TargetStatus.SATISFIED and any(s is not CheckStatus.PASS for s in target_statuses):
        raise ValueError("SATISFIED target status requires every target check to PASS")
    if result.target_status is TargetStatus.UNMET and not has_fail:
        raise ValueError("UNMET target status requires at least one failing target check")
    if result.target_status is TargetStatus.UNKNOWN and (has_fail or not has_unavailable):
        raise ValueError("UNKNOWN target status requires an UNAVAILABLE target check and no failing target check")
