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
