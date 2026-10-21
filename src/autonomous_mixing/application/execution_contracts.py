"""Execution request records for bounded offline gain/full-mix processing (metadata only).

These records describe a requested execution. Constructing them performs no file access,
workspace allocation, locking or processing, and implies no authorization: cross-record
consistency is assessed by ``preflight_execution``.
"""

import re
from dataclasses import dataclass

from autonomous_mixing.application.admission import ActionAdmissionPolicy
from autonomous_mixing.application.contracts import DecisionRequest
from autonomous_mixing.domain.action import ExecutionIssue, ExecutionStatus
from autonomous_mixing.domain.decision import Decision
from autonomous_mixing.domain.observation import RenderSpec
from autonomous_mixing.domain.project import ArtifactKind, AudioArtifact, MixRecipe
from autonomous_mixing.domain.shared import (
    ArtifactId,
    ExecutionId,
    ProjectId,
    Revision,
    TrackId,
    VersionRef,
    require_finite,
    require_instance,
    require_text,
    require_tuple_of,
)

_DIRECTORY_TOKEN = re.compile(r"[A-Za-z0-9_-]+")


@dataclass(frozen=True)
class StemBinding:
    """Explicit selection of the current stem artifact for one recipe contributor."""

    track_id: TrackId
    artifact_id: ArtifactId

    def __post_init__(self) -> None:
        require_instance(self.track_id, TrackId, "StemBinding.track_id")
        require_instance(self.artifact_id, ArtifactId, "StemBinding.artifact_id")


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
        require_instance(self.workspace, ExecutionWorkspace, "ExecutionRequest.workspace")
        require_instance(self.candidate, CandidateIdentity, "ExecutionRequest.candidate")


@dataclass(frozen=True)
class ProcessingPlan:
    """Bounded, resolved input for a future audio processor (data only; no controller context).

    The processor renders ``fixed_target_input`` at ``requested_gain_db`` (absolute additional gain)
    into the new target stem, then sums the mix in ``recipe`` order from ``current_stems``,
    substituting the new target stem for ``target_current_artifact_id``. Current non-target stems
    are already rendered: their gains must not be applied again, and the obsolete current target
    stem must be neither attenuated nor summed alongside the new one.
    """

    execution_id: ExecutionId
    project_id: ProjectId
    before_revision: Revision
    candidate: CandidateIdentity
    target_track_id: TrackId
    fixed_target_input: AudioArtifact
    requested_gain_db: float
    current_stems: tuple[AudioArtifact, ...]
    target_current_artifact_id: ArtifactId
    current_mix_artifact_id: ArtifactId
    recipe: MixRecipe
    render_spec: RenderSpec
    workspace: ExecutionWorkspace

    def __post_init__(self) -> None:
        require_instance(self.execution_id, ExecutionId, "ProcessingPlan.execution_id")
        require_instance(self.project_id, ProjectId, "ProcessingPlan.project_id")
        require_instance(self.before_revision, Revision, "ProcessingPlan.before_revision")
        require_instance(self.candidate, CandidateIdentity, "ProcessingPlan.candidate")
        require_instance(self.target_track_id, TrackId, "ProcessingPlan.target_track_id")
        require_instance(self.fixed_target_input, AudioArtifact, "ProcessingPlan.fixed_target_input")
        require_finite(self.requested_gain_db, "ProcessingPlan.requested_gain_db")
        require_tuple_of(
            self.current_stems, AudioArtifact, "ProcessingPlan.current_stems", nonempty=True, distinct=True
        )
        require_instance(self.target_current_artifact_id, ArtifactId, "ProcessingPlan.target_current_artifact_id")
        require_instance(self.current_mix_artifact_id, ArtifactId, "ProcessingPlan.current_mix_artifact_id")
        require_instance(self.recipe, MixRecipe, "ProcessingPlan.recipe")
        require_instance(self.render_spec, RenderSpec, "ProcessingPlan.render_spec")
        require_instance(self.workspace, ExecutionWorkspace, "ProcessingPlan.workspace")

        if self.workspace.execution_id != self.execution_id:
            raise ValueError("ProcessingPlan workspace belongs to another execution")
        if self.candidate.revision == self.before_revision:
            raise ValueError("ProcessingPlan candidate revision must differ from the before revision")
        stem_tracks = tuple(stem.source_track_ids for stem in self.current_stems)
        if stem_tracks != tuple((track,) for track in self.recipe.track_ids) or any(
            stem.kind is not ArtifactKind.STEM for stem in self.current_stems
        ):
            raise ValueError("ProcessingPlan.current_stems must be one STEM per recipe track, in recipe order")
        if self.target_track_id not in self.recipe.track_ids:
            raise ValueError("ProcessingPlan target track is not a recipe contributor")
        target_stem = self.current_stems[self.recipe.track_ids.index(self.target_track_id)]
        if target_stem.artifact_id != self.target_current_artifact_id:
            raise ValueError("ProcessingPlan.target_current_artifact_id must be the target's current stem")
        fixed = self.fixed_target_input
        if fixed.kind is not ArtifactKind.STEM or fixed.source_track_ids != (self.target_track_id,):
            raise ValueError("ProcessingPlan.fixed_target_input must be a STEM of exactly the target track")
        used = {stem.artifact_id for stem in self.current_stems} | {fixed.artifact_id, self.current_mix_artifact_id}
        if {self.candidate.target_artifact_id, self.candidate.mix_artifact_id} & used:
            raise ValueError("ProcessingPlan candidate artifact IDs must not reuse input artifact IDs")


@dataclass(frozen=True)
class ArtifactProcessingEvidence:
    """Adapter claims about one produced artifact; recorded claims, not independent proof.

    ``processor`` identifies the implementation; it does not imply numerical precision, file
    subtype or summation order, which the later adapter plan must specify.
    """

    artifact_id: ArtifactId
    verified_input_ids: tuple[ArtifactId, ...]
    input_hashes_verified: bool
    finite_samples: bool
    peak_linear: float
    processor: VersionRef

    def __post_init__(self) -> None:
        require_instance(self.artifact_id, ArtifactId, "ArtifactProcessingEvidence.artifact_id")
        require_tuple_of(
            self.verified_input_ids,
            ArtifactId,
            "ArtifactProcessingEvidence.verified_input_ids",
            nonempty=True,
            distinct=True,
        )
        for name in ("input_hashes_verified", "finite_samples"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"ArtifactProcessingEvidence.{name} must be a bool")
        if require_finite(self.peak_linear, "ArtifactProcessingEvidence.peak_linear") < 0:
            raise ValueError("ArtifactProcessingEvidence.peak_linear must be non-negative")
        require_instance(self.processor, VersionRef, "ArtifactProcessingEvidence.processor")


@dataclass(frozen=True)
class ProcessedCandidate:
    """A processor's successful outputs: new target stem, new full mix and their evidence."""

    target_artifact: AudioArtifact
    mix_artifact: AudioArtifact
    evidence: tuple[ArtifactProcessingEvidence, ...]

    def __post_init__(self) -> None:
        require_instance(self.target_artifact, AudioArtifact, "ProcessedCandidate.target_artifact")
        require_instance(self.mix_artifact, AudioArtifact, "ProcessedCandidate.mix_artifact")
        if self.target_artifact.artifact_id == self.mix_artifact.artifact_id:
            raise ValueError("ProcessedCandidate outputs must have distinct artifact IDs")
        require_tuple_of(
            self.evidence, ArtifactProcessingEvidence, "ProcessedCandidate.evidence", nonempty=True, distinct=False
        )
        ids = [record.artifact_id for record in self.evidence]
        if len(set(ids)) != len(ids):
            raise ValueError("ProcessedCandidate.evidence must have one record per artifact")


@dataclass(frozen=True)
class ProcessingFailure:
    """A processor outcome without registered candidate outputs: FAILED (established) or UNCERTAIN.

    Unlike a generic port failure, this keeps known and uncertain outcomes distinct once processing
    may have started. Temporary files may remain; no cleanup is claimed.
    """

    status: ExecutionStatus
    issue: ExecutionIssue

    def __post_init__(self) -> None:
        require_instance(self.status, ExecutionStatus, "ProcessingFailure.status")
        if self.status not in (ExecutionStatus.FAILED, ExecutionStatus.UNCERTAIN):
            raise ValueError("ProcessingFailure.status must be FAILED or UNCERTAIN")
        require_instance(self.issue, ExecutionIssue, "ProcessingFailure.issue")


ProcessingOutcome = ProcessedCandidate | ProcessingFailure


def _check_output(artifact: AudioArtifact, plan: ProcessingPlan, expected_id: ArtifactId, kind: ArtifactKind) -> None:
    label = f"output {artifact.artifact_id}"
    if artifact.artifact_id != expected_id:
        raise ValueError(f"{label} must use the assigned candidate ID {expected_id}")
    if artifact.project_id != plan.project_id:
        raise ValueError(f"{label} belongs to project {artifact.project_id}, not {plan.project_id}")
    if artifact.revision != plan.candidate.revision:
        raise ValueError(
            f"{label} has revision {artifact.revision}, not the candidate revision {plan.candidate.revision}"
        )
    if artifact.kind is not kind:
        raise ValueError(f"{label} must have kind {kind.name}")
    reference = plan.fixed_target_input
    expected = (plan.render_spec.sample_rate_hz, plan.render_spec.channel_count, reference.frame_count)
    actual = (artifact.sample_rate_hz, artifact.channel_count, artifact.frame_count)
    if actual != expected or artifact.timeline_start_seconds != reference.timeline_start_seconds:
        raise ValueError(f"{label} dimensions differ from the plan's input and render settings")
    if artifact.render_spec != plan.render_spec.ref:
        raise ValueError(f"{label} render spec {artifact.render_spec} differs from the plan's {plan.render_spec.ref}")


def validate_processed_candidate(plan: ProcessingPlan, response: ProcessedCandidate) -> None:
    """Check a processor's outputs and evidence against the plan (structure only).

    Does not verify files, hashes, sample values, workspace membership or path/alias safety, and
    assembles no receipt or state; evidence flags are adapter claims. Location checks are lexical and
    cover the plan's inputs only (the plan carries the current mix's ID, not its location).
    """
    require_instance(plan, ProcessingPlan, "plan")
    require_instance(response, ProcessedCandidate, "response")
    target, mix = response.target_artifact, response.mix_artifact
    _check_output(target, plan, plan.candidate.target_artifact_id, ArtifactKind.STEM)
    _check_output(mix, plan, plan.candidate.mix_artifact_id, ArtifactKind.MIX)
    if target.source_track_ids != (plan.target_track_id,):
        raise ValueError(f"target output source tracks must be exactly ({plan.target_track_id},)")
    if set(mix.source_track_ids) != set(plan.recipe.track_ids):
        raise ValueError("mix output source tracks must equal the recipe contributors")

    evidence = {record.artifact_id: record for record in response.evidence}
    if set(evidence) != {target.artifact_id, mix.artifact_id}:
        raise ValueError("evidence must contain exactly one record per output artifact")
    for record in evidence.values():
        if not (record.input_hashes_verified and record.finite_samples):
            raise ValueError(f"evidence for {record.artifact_id} does not claim verified inputs and finite samples")
    if evidence[target.artifact_id].processor != evidence[mix.artifact_id].processor:
        raise ValueError("both outputs must cite the same processor")
    if set(evidence[target.artifact_id].verified_input_ids) != {plan.fixed_target_input.artifact_id}:
        raise ValueError("target evidence must cite exactly the fixed target input")
    non_target = {s.artifact_id for s in plan.current_stems if s.artifact_id != plan.target_current_artifact_id}
    if set(evidence[mix.artifact_id].verified_input_ids) != {target.artifact_id} | non_target:
        raise ValueError("mix evidence must cite exactly the new target stem and the current non-target stems")

    input_locations = {plan.fixed_target_input.location} | {stem.location for stem in plan.current_stems}
    if target.location == mix.location or {target.location, mix.location} & input_locations:
        raise ValueError("output locations must differ from each other and from every input location (lexical check)")
