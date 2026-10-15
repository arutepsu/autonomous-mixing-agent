# Instructions for Claude

This repository is a bachelor-thesis research prototype, not a production DAW. Read `README.md`, `docs/research/project-scope.md`, `docs/architecture/overview.md`, `docs/project/requirements.md`, `docs/research/methodology.md`, and `docs/project/documentation-policy.md` before changing behavior.

## Priorities
1. Scientific validity, traceability and maintainability over demos ([ADR-006](docs/decisions/0006-research-first-development-policy.md)): no artificial end-to-end examples, generated example music or temporary features; every feature traces to a documented requirement; keep the architecture track-role-agnostic (not kick/bass-specific); implement problem-specific features (e.g. masking) only in their roadmap phase; no hardcoded musical assumptions or arbitrary thresholds. Never equate overlap features with proven perceptual masking.
2. Make small, testable changes with deterministic DSP and validated inputs.
3. The model proposes actions; application code validates, executes and verifies them.
4. Keep original WAV files immutable. Never commit credentials or copyrighted stems.
5. Write regression tests for algorithm changes and run relevant tests after edits. Synthetic numerical signals are for unit tests only, never evaluation data. Validate changes via imports, CLI registration and tests, not demo runs.
6. Do not delete existing demo scripts or data without reviewing their dependencies and getting owner approval.

## Documentation rules
- `docs/research/research-log.md` is append-only: add timestamped entries, never rewrite earlier ones.
- ADRs live in `docs/decisions/`, one file each, indexed in its `README.md`. Never edit an accepted ADR; supersede it with a new one.
- For other docs, edit the relevant section in place while preserving unrelated details; state any superseded conclusions explicitly.
- Update `docs/project/roadmap.md` only for actual scope or status changes; do not mark work done without evidence.
- Put scientific uncertainties under "Open questions" rather than presenting guesses as facts.
- For architectural changes, add a new ADR file in `docs/decisions/` (template in its README) with rationale and consequences, and add it to the index.
- If documents conflict, point out the conflict; do not silently select one.
- Never regenerate all Markdown files as a side effect of implementing a feature.

## Naming ([ADR-005](docs/decisions/0005-system-oriented-naming.md))
Repository/distribution `autonomous-mixing-system`, import package `autonomous_mixing`, CLI `autonomous-mixing`. Use "agent" only for the AI decision component (`decision_agent`, planned) and in the thesis title; never rename the thesis title.

## Project commands
`uv sync --group dev` / `uv run pytest -q` / `uv run ruff check .` / `uv run autonomous-mixing --help`.
Never use `pip install` or `uv init` here; change dependencies via `uv add` and keep `uv.lock` in sync. Status labels for docs are defined in `docs/project/documentation-policy.md`.

## State
M0 implements descriptive WAV analysis only. Detection, corrections and Claude orchestration are planned, not yet implemented. The M0 interface still labels its inputs kick/bass; this is a known deviation under review (ADR-006), not a pattern to extend.
