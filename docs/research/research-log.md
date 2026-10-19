# Research log
## 2026-10-14
- Repository starter created.
- M0 descriptive analysis only; masking metric pending literature and calibration.

## 2026-10-14 — repository preparation
- Named project `autonomous-mixing-agent`; Python import package remains `mixing_agent`.
- Adopted uv conventions and prepared structured documentation for Claude collaboration.
- Existing analyzer behavior remains unchanged; uv lock resolution and tests on a freshly synced uv environment still need local verification.

## 2026-10-14 — environment and M0 workflow verification
- Follows up the open item from the previous entry: `uv lock` resolved 31 packages (including the optional `agent` extra, which is locked but not installed by default); `uv sync --group dev` installed 14 packages on CPython 3.11.17; `uv lock --check` and `uv sync --locked` pass. uv 0.13.1 was run from a temporary virtual environment because uv is not yet installed on the development machine's PATH.
- Test suite before changes: 5 passed. After adding loader and CLI tests: 17 passed. `ruff check .` clean with the project-pinned rule set.
- Synthetic stems regenerated with `scripts/generate_test_audio.py`; the CLI report is identical to the previously stored `results/analysis.json` (same SHA-256 input hashes and feature values), so the synthetic generator and analysis are deterministic on this machine.
- Observed values on synthetic stems (descriptive only, no perceptual meaning): kick RMS −18.66 dBFS / peak −3.33 dBFS; bass RMS −19.25 dBFS / peak −14.90 dBFS; temporal coactivity fraction 0.164.
- Invalid-input checks previously surfaced as Python tracebacks (missing file reported only as "System error"). The CLI now reports validation errors as one-line messages with exit code 2; mismatch messages include the offending sample rates / frame counts. Analysis results are unchanged.
- The project directory is not yet a Git repository; no commit has been made.

## 2026-10-15 — naming migration to `autonomous-mixing-system`
- Supersedes the naming note of the 2026-10-14 "repository preparation" entry; see ADR-005. Import package renamed `mixing_agent` → `autonomous_mixing`, CLI `mixing-agent` → `autonomous-mixing`, distribution `autonomous-mixing-agent` → `autonomous-mixing-system`. Module contents unchanged apart from the CLI program name.
- Verification (uv 0.13.1, again from a temporary virtual environment; CPython 3.11.17): `uv sync --group dev` replaced the editable install; `uv lock --check` passes (lockfile changed only in the project name); 17 tests pass; `ruff check .` clean; `mixing_agent` is no longer importable; the `autonomous-mixing` entry point resolves to `autonomous_mixing.cli:main`.
- Regenerated synthetic stems and the CLI report are byte-identical to those from before the migration (same SHA-256), so analysis behavior is unchanged.
- GitHub repository renamed to `arutepsu/autonomous-mixing-system` and `origin` updated; `git ls-remote origin` succeeds. The local working directory is renamed separately by the owner.

## 2026-10-15 — research-first development policy; migration re-validation
- Owner policy correction recorded as ADR-006. Correction to the previous entry: regenerating the synthetic stems and re-running the CLI on them was a demo run, not a required validation step; it is not repeated here.
- The project `.venv` was stale after the working-directory rename: the editable install still pointed to `...\autonomous-mixing-agent\src` and console-script trampolines failed ("uv trampoline failed to canonicalize script path"), so imports and `pytest` failed. Fixed with `uv sync --group dev --locked --reinstall` (uv 0.13.1 from a temporary virtual environment; uv is still not on PATH).
- Validation after re-sync (CPython 3.11.17): `uv lock --check` passes (lockfile diff vs. last commit: project name only); all `autonomous_mixing` modules import; `mixing_agent` is not importable; distribution `autonomous-mixing-system` 0.1.0 registers `autonomous-mixing = autonomous_mixing.cli:main`; `autonomous-mixing --help` exits 0; 17 tests pass; `ruff check .` clean.
- Demo-asset review (nothing deleted): `scripts/generate_test_audio.py` (tracked) is not used by any test, as the tests synthesize their own signals; `data/synthetic/kick.wav`, `data/synthetic/bass.wav` and `results/analysis.json` are untracked, gitignored outputs of earlier demo runs. Disposition pending owner approval (see `architecture.md` open questions).
- Known ADR-006 deviations in M0 code, retained unchanged: kick/bass-named inputs (CLI, `analyze_pair`, report keys) and hardcoded 30–200 Hz band and 10 % activity threshold.

## 2026-10-15 — documentation restructured into topic folders
- Implemented ADR-007: `docs/` now has `decisions/` (one file per ADR plus index), `architecture/overview.md`, `research/` and `project/`. Files were moved with `git mv`; ADR-001 to ADR-006 were copied verbatim from `decisions.md` (heading level only). Paths in earlier entries of this log refer to the previous flat layout.
- Links in `README.md`, `CLAUDE.md` and the living documents were updated; all relative Markdown links were checked to resolve. No code or behavior changed.

## 2026-10-15 — Requirements Specification v1.0
- Researcher approved the consolidated Requirements Specification v1.0 (`docs/project/requirements.md`), replacing the unapproved v1 draft. Requirements are stated technology-neutrally; no architectural alternative (state representation, class structure, orchestration framework) was decided.
- Main changes: multitrack project input (FR-01); compatibility and alignment required, with the resampling/alignment policy left open (FR-02, D3); uncertainty representable without assuming calibrated confidence (FR-05, D11); action types and bounds deferred (FR-08, D5); per-family depth for P1–P3 (FR-13); new comparison, evaluation, provenance and safety requirements (FR-15 to FR-18, QR-07, QR-08, SR-01 to SR-09, OP-01 to OP-05). SR-01 requires each comparison to name its independent variables and document confounders; equal action budgets alone are not treated as sufficient.
- Corrected the overstated M0 status (WAVEX/RF64 were marked "tested" without a test). Under the v1.0 wording the M0 exit criteria are not met (multitrack input, full configuration recording and numeric feature tests are missing).
- Thesis title corrected to "Autonomous Detection and Correction of Mixing Problems Using an AI Agent" in `README.md` and `project-scope.md`.
- Scope clarified: P1, P2 and P3 remain planned research targets; P1 end-to-end is the contingency minimum, not a decision to abandon P2/P3 (`project-scope.md`, roadmap priority 3).
- ADR-008 clarifies ADR-006 point 6: controlled defect injection into real stems is permitted; artificially generated music is not evaluation data.
- Documentation only; no code, tests or audio changed.

## 2026-10-15 — development agent team aligned with the offline WAV baseline
- Added five development-assistant role definitions (mixing-coordinator, mixing-engineer, mixing-dsp, mixing-evaluator, thesis-supporter) for Claude Code (`.claude/agents/`) and Codex (`.codex/agents/`), plus `agent-team/PROJECT_BRIEF.md` and `agent-team/README.md`. They are assistants for thesis development, not part of the runtime system (ADR-004 unaffected).
- The prepared configuration followed the Source of Truth document v0.1, which proposes an FL Studio prototype with an early FL Studio feasibility milestone and conflicts with ADR-001, `requirements.md` (FR-14 withdrawn) and `project-scope.md`. Owner resolved this on 2026-10-15; recorded as ADR-009: the offline Python/WAV workflow is the implementation baseline, and FL Studio integration is deferred and optional. ADR-001 and the reference documents are unchanged.
- Remaining differences between the document and the repository stay open and are listed in `agent-team/PROJECT_BRIEF.md`: hypotheses (context sensitivity, abstention), comparison design versus B0–B3 (D7), context-priority cases, P2/P3 depth, a hidden-reference requirement not yet stated in `requirements.md`, and milestone numbering.
- Verification: structural checks of all ten definitions passed (required fields; matching Claude/Codex text). Runtime discovery by either client has not been confirmed. Configuration only; no code, tests or audio changed.

## 2026-10-15 — hidden-reference boundary documented; brief references restored
- Recorded the hidden-reference boundary as ADR-010 and requirement SR-10 (requirements v1.1) at the owner's instruction. Original reference audio and defect-injection ground truth are unavailable to every controller, its decision inputs and runtime validation; they are stored separately and joined with run records only after execution. The ordinary action history remains runtime information.
- Correction to the earlier requirements wording: FR-18 had propagated defect-injection parameters into run records; it now keeps them out and links them only by identifiers. FR-12, the system-context inputs/outputs, `dataset-plan.md` (leakage prevention), `architecture/overview.md` (target pipeline), `agent-team/PROJECT_BRIEF.md` and the mixing-evaluator role (Claude and Codex) were aligned. ADR-008 is refined, not edited (index status updated); the hidden-reference item ADR-009 listed as open is closed.
- `agent-team/PROJECT_BRIEF.md`: the three reference-document paths, which had been removed, were restored after verifying the files exist at their original locations; no repository copies exist.
- Documentation and configuration only; no code, tests or audio changed. Other Source of Truth conflicts remain open.
