# AI Mixing Agent project reference

Read the repository's CLAUDE.md first; its documentation and development rules apply to every role. Treat the following reference documents as read-only:

These paths are outside the repository and local to the owner's computer; no repository copies exist. In another environment, ask for the actual documents. This brief is a navigation aid, not a replacement for the full reference. Earlier PROJECT_CONTEXT.md and TEAM_PROMPTS.md (ChatGPT project mirror, intentionally not copied into this repository) are provisional and contain outdated scope assumptions; prefer the reference documents listed here and this team configuration.

## Implementation baseline (confirmed, ADR-009)

The repository's accepted decisions govern implementation: ADRs in docs/decisions/, docs/project/requirements.md, docs/research/project-scope.md and docs/project/roadmap.md. The Source of Truth document remains the main reference for the thesis concept, but it is a proposed design (v0.1), not completed implementation.

- Offline Python processing of aligned WAV stems with declared track roles, via the CLI (ADR-001). FL Studio is used to compose and export stems (docs/research/dataset-plan.md).
- FL Studio integration is deferred and optional. It is not scheduled; .flp manipulation is excluded from the current requirements (FR-14 withdrawn). Investigate it only when the owner explicitly assigns it; adopting it would need a new requirement and ADR.
- One runtime AI agent (decision_agent, planned) proposes structured actions; deterministic application code validates, executes and verifies them (ADR-004, OP-01).

## Thesis invariants

Keep these regardless of the integration route:

- Research question: Autonomous Detection and Correction of Mixing Problems Using an AI Agent. The repository wording (main RQ, RQ1–RQ4, H1–H3) is in project-scope.md.
- Problem families: P1 spectral/temporal masking, with kick–bass as the primary use case rather than an architectural assumption; P2 buildup/resonance and P3 stereo/phase are planned research targets (project-scope.md). This is mixing research, not note correction, composition, mastering, or a claim of universal aesthetic improvement.
- Fair controller comparison: conditions B0–B3 (SR-01) with a credible deterministic baseline. Each comparison names its independent variables and holds inputs, measurements, context, action capabilities, validation and budgets otherwise equal.
- Deterministic validation; bounded, allowlisted and reversible actions (FR-07, FR-08, QR-04); explicit abstention or insufficient-evidence outcomes (FR-06); exact rollback (FR-10).
- Hidden evaluation reference (SR-10, ADR-010): original reference audio and defect-injection ground truth are unavailable to every controller, its decision inputs and runtime validation. They are stored separately and used only after the run for research evaluation, where a combined report may join them with run records. The ordinary action history of a run is runtime information, not hidden data.
- Calibrate metrics and thresholds on the calibration split and freeze them before evaluation (SR-02). Overlap is a proxy for possible masking, not proof of a perceptual defect (SR-08).

## Reading the Source of Truth document

The document labels statements as proposal baseline, engineering proposal or research decision pending (its reading conventions; open decisions and decision log in sections 14–15). Keep these labels when citing it, and do not convert suggestions into accepted decisions. Its FL Studio adapter, FL Studio feasibility milestone, suggested repository layout and stack are engineering proposals superseded for implementation by the baseline above.

## Development assistants versus the runtime system

The five roles in .claude/agents/ and .codex/agents/ help develop the thesis. They are not the runtime mixing system, not its decision_agent and not a controller under evaluation. ADR-004's single-agent, no-multi-agent rule concerns the runtime system and is unaffected.

## Remaining research conflicts (open; owner decides)

Report these when relevant; do not resolve them silently:

1. Hypotheses: the document's H1 context sensitivity and H4 abstention are not explicit repository hypotheses. The repository's H1–H3 cover improvement, iteration and constraints.
2. Comparison design: the document compares an LLM controller with a rule-based controller and suggests an optional context-aware baseline. The repository requires B0–B3 and leaves the rule design to open decision D7.
3. Context-sensitivity cases: the document's kick-priority, bass-priority and unknown-priority conditions, and its cases with existing sidechain, have no repository counterpart. In a WAV workflow, existing processing is not observable from DAW state, so it would have to be declared (D4, D6).
4. P2/P3 depth: the document treats them as extensions under time pressure. project-scope.md v1.0 explicitly supersedes "extension"; P1 end-to-end is only the contingency minimum (D2).
5. Hidden reference: resolved on 2026-10-15 by ADR-010 and requirement SR-10 (FR-18 revised); no longer open.
6. Milestones: the document's M0–M6 differ from the repository roadmap's M0–M9; the roadmap governs scheduling.

## Shared work rules

- The human chooses research direction and musical intent. Do not invent missing intent.
- The main chat coordinates. Specialist agents are development assistants, separate from the runtime mixing system and the controllers under evaluation.
- Every assignment identifies goal, inputs, permitted files, output, acceptance criteria and dependencies.
- Delegate only when requested or when applicable project/skill instructions authorize it. Avoid recursive delegation unless explicitly assigned.
- Research-only tasks do not authorize implementation or source edits.
- Never modify source audio (QR-01); write corrections and renders as new outputs with restoration state, and never overwrite earlier runs (OP-02).
- Keep concurrent writes in distinct files or isolated worktrees. Codex and Claude do not automatically share conversation memory; communicate through explicit task briefs and saved handoffs.
- Verify sources and results. Never fabricate experiments, citations, listening observations or success claims.
- Return outcome, artifacts, evidence/verification, limitations, pending decisions and next handoff. Separate proposals from confirmed decisions.
- Prompt instructions do not replace enforced tool bounds or permission controls.
