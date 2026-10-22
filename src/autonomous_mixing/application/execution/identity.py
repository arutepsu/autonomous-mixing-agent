"""Execution identity records shared by execution requests and processing plans (metadata only).

Kept separate so that requests and processing records both depend on these identities without
importing each other. Constructing them performs no file access or allocation.
"""

import re
from dataclasses import dataclass

from autonomous_mixing.domain.shared import ArtifactId, ExecutionId, Revision, require_instance, require_text

_DIRECTORY_TOKEN = re.compile(r"[A-Za-z0-9_-]+")


@dataclass(frozen=True)
class ExecutionWorkspace:
    """Logical, application-issued output workspace assignment for one execution.

    ``root_key`` names configured storage, not a path; ``directory_token`` is a restricted logical
    name. Physical allocation, existence, collision and alias checks are deferred to the file adapter.
    """

    execution_id: ExecutionId
    root_key: str
    directory_token: str

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "ExecutionWorkspace.execution_id")
        require_text(self.root_key, "ExecutionWorkspace.root_key")
        if not isinstance(self.directory_token, str) or not _DIRECTORY_TOKEN.fullmatch(self.directory_token):
            raise ValueError("ExecutionWorkspace.directory_token must match [A-Za-z0-9_-]+")


@dataclass(frozen=True)
class CandidateIdentity:
    """Application-assigned identities for the candidate state and its new target stem and mix."""

    revision: Revision
    target_artifact_id: ArtifactId
    mix_artifact_id: ArtifactId

    def __post_init__(self) -> None:
        require_instance(self.revision, Revision, "CandidateIdentity.revision")
        require_instance(self.target_artifact_id, ArtifactId, "CandidateIdentity.target_artifact_id")
        require_instance(self.mix_artifact_id, ArtifactId, "CandidateIdentity.mix_artifact_id")
        if self.target_artifact_id == self.mix_artifact_id:
            raise ValueError("CandidateIdentity target and mix artifact IDs must differ")
