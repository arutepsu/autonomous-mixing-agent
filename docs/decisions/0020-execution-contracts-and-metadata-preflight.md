# ADR-020 — offline execution contracts and deterministic metadata preflight (2026-10-21)
- Status: Proposed; awaiting owner review of the implementing stage.
- Decision: define the first stage of bounded offline gain execution. It covers a versioned full-mix recipe, explicit execution request records, a pure metadata preflight, a processing port and structural response checks. No DSP, file operations, workspace allocation, locks or execution service exist yet.
  1. Mix construction for the supported D4 subset: `domain.project.MixRecipe(reference, track_ids, summing_policy)` names unique logical contributors in summation order. `SummingPolicy.SAMPLE_SUM` is sample-wise addition of current stems without automatic normalization, limiting or clipping. The first execution operation rebuilds the full mix from every snapshot track exactly once. That is a restriction of this operation, not of all project states, and it claims no equivalence to an original producer mix.
  2. Request records in `application.execution_contracts`:
     - `StemBinding(track_id, artifact_id)`: an explicit current stem per contributor, never guessed from names.
     - `ExecutionWorkspace(execution_id, root_key, directory_token)`: a logical, application-issued assignment; `root_key` names configured storage, not a path, and the token matches `[A-Za-z0-9_-]+`.
     - `CandidateIdentity(revision, target_artifact_id, mix_artifact_id)`: application-assigned and distinct.
     - `ExecutionRequest(execution_id, decision_request, decision, policy, mix_recipe, stem_bindings, current_mix_artifact_id, render_spec, workspace, candidate)`: reuses the decision request's single `ProjectState`. Construction checks types and binding uniqueness only.
  3. `preflight_execution(request) -> MetadataReady | PreflightRejected` is pure: it invokes no processor and touches no file. The first failure wins:
     1. `admit_action` is rerun (an earlier admission is not a capability token), and its rejection is kept unchanged under `ADMISSION_REJECTED`; an abstention yields no receipt or invented action ID;
     2. the workspace belongs to this execution (`INVALID_WORKSPACE`);
     3. the candidate revision is new and the candidate IDs are disjoint from current audio and fixed baselines (`INVALID_CANDIDATE_IDENTITY`); (Clarified 2026-10-21, audit F5: "new" means absent from `ProjectState.known_revisions`, which covers the current revision and the production revisions of audio members and fixed baselines; global uniqueness is deferred to identity allocation and a ledger.)
     4. the recipe equals the snapshot inventory, and the bindings cover it exactly with STEM members of exactly their track (`INVALID_RECIPE_BINDINGS`);
     5. the selected current mix is a MIX member whose contributors equal the recipe's as a set (`INVALID_MIX`);
     6. the target has an explicit gain state (`MISSING_GAIN_STATE`);
     7. mapped stems, the fixed target input and the selected mix share sample rate, channels, a non-zero frame count and timeline start, matching the render rate and channels (`INCOMPATIBLE_AUDIO`); shared metadata is not proof of alignment (D3);
     8. every current artifact depending on the target is the selected target stem or mix, so affected groups and alternate stems or mixes are never silently retained (`UNSUPPORTED_DEPENDENCY`).
  4. `MetadataReady.plan: ProcessingPlan` carries only the data the processor needs. It separates the fixed target input (rendered at the requested absolute gain) from already-rendered current stems in recipe order. The new target stem replaces the current one in the sum, so non-target gains are never applied twice and the obsolete target is neither attenuated nor summed. The plan is checked for structural self-consistency when constructed.
  5. Processing port: `AudioProcessor.process(plan) -> ProcessedCandidate | ProcessingFailure` is a non-runtime-checkable Protocol with no implementation.
     - `ProcessingFailure` allows only FAILED or UNCERTAIN, keeping known and uncertain outcomes distinct after processing may have started.
     - `ArtifactProcessingEvidence` records adapter claims: verified input IDs, hash and finite-sample flags, a finite non-negative peak and the processor `VersionRef`.
     - `validate_processed_candidate(plan, response)` requires, for both outputs:
       - the assigned IDs, project and candidate revision;
       - STEM and MIX kinds, with exact target track and recipe contributors as a set;
       - the plan's dimensions, and `render_spec` equal to `plan.render_spec.ref`;
       - one evidence record each, all flags true and the same processor;
       - the target citing exactly the fixed input, and the mix exactly the new target plus the non-target current stems;
       - output locations lexically distinct from each other and from the plan's input locations.
- Source: owner-approved offline execution design and execution-preflight plan (2026-10-21), with the owner's confirmations of 2026-10-21: mix sources compare as a set while summation order follows the recipe; both outputs must cite `plan.render_spec.ref`; `MixRecipe` and `SummingPolicy` are exported through `domain.project` and the root compatibility interface.
- Rationale: an explicit recipe, explicit bindings and a fixed check order make execution inputs traceable and deterministic (FR-08, FR-17, QR-02). Rerunning admission keeps rejected or protected proposals from executing (FR-07, OP-01). Rejecting undeclared target-dependent outputs prevents stale audio from surviving a correction (FR-09). Separating the fixed input from current stems implements fixed-input gain semantics without double gain (ADR-019).
- Consequences:
  - Partial groundwork for FR-07, FR-08, FR-09, FR-17, QR-01, QR-02, QR-07 and SR-10; none is met. Requirement statuses are unchanged.
  - `MetadataReady` proves no file integrity or hashes, sample alignment, authorization against later-changed external state, safe or collision-free workspace allocation, or exclusive access. Evidence flags are adapter claims. The location check is lexical only and does not cover the current mix's location, which the plan carries only by ID.
  - Deferred to reviewed later stages:
    - the DSP adapter, which must pin numerical precision, float WAV subtype and summation order before implementation;
    - file and hash verification, path, alias and symlink safety, and atomic workspace creation with collision handling;
    - exclusive execution access, receipt and candidate-state assembly in an execution service, and failure accounting;
    - budget enforcement and render reservations, and a durable execution ledger with restart reconciliation.
  - Group processing, subset mixes, dependency graphs, resampling and time alignment are unsupported.
