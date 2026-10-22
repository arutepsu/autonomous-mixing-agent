"""Execution request records for bounded offline gain/full-mix processing (metadata only).

These records describe a requested execution. Constructing them performs no file access,
workspace allocation, locking or processing, and implies no authorization: cross-record
consistency is assessed by ``preflight_execution``.
"""

from dataclasses import dataclass

from autonomous_mixing.application.admission import ActionAdmissionPolicy
from autonomous_mixing.application.decision import DecisionRequest
from autonomous_mixing.application.execution.identity import CandidateIdentity, ExecutionWorkspace
from autonomous_mixing.domain.decision import Decision
from autonomous_mixing.domain.observation import RenderSpec
from autonomous_mixing.domain.project import MixRecipe, ProcessingSpec
from autonomous_mixing.domain.shared import ArtifactId, ExecutionId, TrackId, require_instance, require_tuple_of


@dataclass(frozen=True)
class StemBinding:
    """Explicit selection of the current stem artifact for one recipe contributor."""

    track_id: TrackId
    artifact_id: ArtifactId

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "StemBinding.track_id")
        require_instance(self.artifact_id, ArtifactId, "StemBinding.artifact_id")


@dataclass(frozen=True)
class ExecutionRequest:
    """A requested execution of one decision's gain action, rebuilding the target stem and full mix.

    The current state is ``decision_request.state``. Construction checks field types and binding
    uniqueness only; all cross-record checks happen in ``preflight_execution``.
    """

    execution_id: ExecutionId
    decision_request: DecisionRequest
    decision: Decision
    policy: ActionAdmissionPolicy
    mix_recipe: MixRecipe
    stem_bindings: tuple[StemBinding, ...]
    current_mix_artifact_id: ArtifactId
    render_spec: RenderSpec
    processing_spec: ProcessingSpec
    workspace: ExecutionWorkspace
    candidate: CandidateIdentity

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "ExecutionRequest.execution_id")
        require_instance(self.decision_request, DecisionRequest, "ExecutionRequest.decision_request")
        require_instance(self.decision, Decision, "ExecutionRequest.decision")
        require_instance(self.policy, ActionAdmissionPolicy, "ExecutionRequest.policy")
        require_instance(self.mix_recipe, MixRecipe, "ExecutionRequest.mix_recipe")
        require_tuple_of(
            self.stem_bindings, StemBinding, "ExecutionRequest.stem_bindings", nonempty=True, distinct=False
        )
        tracks = [binding.track_id for binding in self.stem_bindings]
        artifacts = [binding.artifact_id for binding in self.stem_bindings]
        if len(set(tracks)) != len(tracks):
            raise ValueError("ExecutionRequest.stem_bindings must bind each track at most once")
        if len(set(artifacts)) != len(artifacts):
            raise ValueError("ExecutionRequest.stem_bindings must bind each artifact at most once")
        require_instance(self.current_mix_artifact_id, ArtifactId, "ExecutionRequest.current_mix_artifact_id")
        require_instance(self.render_spec, RenderSpec, "ExecutionRequest.render_spec")
        require_instance(self.processing_spec, ProcessingSpec, "ExecutionRequest.processing_spec")
        require_instance(self.workspace, ExecutionWorkspace, "ExecutionRequest.workspace")
        require_instance(self.candidate, CandidateIdentity, "ExecutionRequest.candidate")
