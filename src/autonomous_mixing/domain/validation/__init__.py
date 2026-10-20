"""Validation component: criteria definitions, recorded results and their consistency check.

No evaluator, metric formulas or thresholds are defined here.
"""

from autonomous_mixing.domain.validation.consistency import validate_validation_references
from autonomous_mixing.domain.validation.criteria import (
    AbsoluteGuard,
    BaselineReference,
    ComparisonOperator,
    DeltaGuard,
    ImprovementCondition,
    ImprovementDirection,
    MetricSelector,
    TargetCondition,
    ValidationCriteria,
)
from autonomous_mixing.domain.validation.result import (
    AssessmentMode,
    CheckResult,
    CheckStatus,
    TargetStatus,
    ValidationResult,
    ValidationVerdict,
)

__all__ = [
    "MetricSelector",
    "ComparisonOperator",
    "ImprovementDirection",
    "BaselineReference",
    "TargetCondition",
    "ImprovementCondition",
    "AbsoluteGuard",
    "DeltaGuard",
    "ValidationCriteria",
    "AssessmentMode",
    "CheckStatus",
    "ValidationVerdict",
    "TargetStatus",
    "CheckResult",
    "ValidationResult",
    "validate_validation_references",
]
