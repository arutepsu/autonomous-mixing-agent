# Autonomous Mixing Agent

Bachelor thesis research prototype: **Autonomous Detection and Correction of Mixing Problems Using AI Agents**.

**Status:** M0 descriptive kick/bass analyzer; autonomous corrections and perceptual masking detection are **not implemented**. Official project period: 2026-10-19 to 2027-01-18.

## Setup (Windows PowerShell)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. This repository already has a `pyproject.toml`; do **not** run `uv init` in it.

```powershell
uv python install 3.11
uv sync --group dev
uv run python scripts/generate_test_audio.py
uv run mixing-agent analyze data/synthetic/kick.wav data/synthetic/bass.wav --output results/analysis.json
uv run pytest -q
uv run ruff check .
```

`uv.lock` pins the resolved dependency set and should be committed; after changing dependencies run `uv lock` and commit the updated lockfile. Use `uv sync --group dev --locked` to fail instead of silently re-resolving.

Optional future Claude SDK dependencies: `uv sync --group dev --extra agent`. Copy `.env.example` to `.env` for secrets and **never commit `.env`**; provider integration is not yet implemented.

## CLI

`mixing-agent analyze KICK.wav BASS.wav [--output PATH]` writes a JSON report (default `results/analysis.json`). Invalid or incompatible inputs (missing file, non-WAV container, unreadable file, fewer than 2048 frames, more than two channels, non-finite samples, differing sample rates or frame counts) are reported as a one-line `error: …` message on stderr with exit code 2.

## Existing measurements and limitations

All values are descriptive measurements, **not** a perceptual masking measurement or validated defect detection.

- `rms_dbfs` and `peak_dbfs` are full-scale levels over all channels; silent signals report minus infinity as `null`.
- `low_band_power_proxy` is the per-frame sum of squared STFT magnitudes (SciPy default `spectrum` scaling, Hann window) in 30–200 Hz, averaged over frames; it is not normalized or calibrated signal power. With 2048-sample frames at 44.1 kHz the band contains only 8 frequency bins (≈21.5 Hz spacing).
- `temporal_coactivity_fraction` is the fraction of STFT frames in which both stems' **full-band** frame energy exceeds 10 % of that stem's own maximum frame energy; **not a validated masking metric**.
- Stereo stems are folded to mono (channel mean) before the STFT; phase cancellation in the fold-down is not detected.
- Synthesized examples do **not** provide perceptual ground truth.

Assumptions behind these parameters are listed in [`docs/methodology.md`](docs/methodology.md#assumptions-requiring-validation).

## Documentation map

This table is the canonical topic-ownership list; change rules are in `docs/documentation-policy.md`.

| File | Authority |
| --- | --- |
| `CLAUDE.md` | Claude operating rules and navigation |
| `docs/project-scope.md` | Research questions, hypotheses, scope and exclusions |
| `docs/requirements.md` | Functional / nonfunctional requirements and acceptance criteria |
| `docs/architecture.md` | Current components, boundaries and target architecture |
| `docs/methodology.md` | Evaluation design and scientific safeguards |
| `docs/dataset-plan.md` | Audio data creation, metadata and partitioning |
| `docs/roadmap.md` | Milestones, dates, priorities and exit criteria |
| `docs/decisions.md` | Append-only architectural decision history |
| `docs/research-log.md` | Append-only research and implementation observations |
| `docs/documentation-policy.md` | Which documents may change and how |

## Current development order

1. Validate M0 audio I/O and feature extraction.
2. Research a published masking-related methodology and define controlled cases.
3. Define typed detector output and independent evaluation criteria.
4. Implement bounded, reversible gain/EQ actions.
5. Introduce Claude as a structured action *proposer*, never as an audio processing tool.

See `docs/roadmap.md`. No FL Studio `.flp` project manipulation is required for the core experiment.
