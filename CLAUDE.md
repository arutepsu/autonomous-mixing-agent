# Instructions for Claude

This repository is a bachelor-thesis research prototype, not a production DAW. Read `README.md`, `docs/project-scope.md`, `docs/architecture.md`, `docs/requirements.md`, `docs/methodology.md`, and `docs/documentation-policy.md` before changing behavior.

## Priorities
1. Scientific validity over impressive demos. Never equate overlap features with proven perceptual masking.
2. Make small, testable changes with deterministic DSP and validated inputs.
3. The model proposes actions; application code validates, executes and verifies them.
4. Keep original WAV files immutable. Never commit credentials or copyrighted stems.
5. Write regression tests for algorithm changes and run relevant tests after edits.

## Documentation rules
- Do not overwrite or rewrite `docs/research-log.md` or `docs/decisions.md`; append timestamped entries.
- For other docs, edit the relevant section in place while preserving unrelated details; state any superseded conclusions explicitly.
- Update `docs/roadmap.md` only for actual scope or status changes; do not mark work done without evidence.
- Put scientific uncertainties under "Open questions" rather than presenting guesses as facts.
- For architectural changes, record an ADR in `docs/decisions.md` with rationale and consequences.
- If documents conflict, point out the conflict; do not silently select one.
- Never regenerate all Markdown files as a side effect of implementing a feature.

## Project commands
`uv sync --group dev` / `uv run pytest -q` / `uv run ruff check .` / `uv run mixing-agent --help` / `uv run python scripts/generate_test_audio.py`.
Never use `pip install` or `uv init` here; change dependencies via `uv add` and keep `uv.lock` in sync. Status labels for docs are defined in `docs/documentation-policy.md`.

## State
M0 implements descriptive WAV analysis only. Detection, corrections and Claude orchestration are planned, not yet implemented.
