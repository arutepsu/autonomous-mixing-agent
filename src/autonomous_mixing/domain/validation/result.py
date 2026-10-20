"""Recorded validation outcomes: check results, verdicts and target status (supplied, not computed)."""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.shared import (
    ConditionId,
    CriteriaId,
    ObservationId,
    ValidationResultId,
    require_instance,
    require_text,
    require_tuple_of,
)


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
