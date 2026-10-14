# Architecture

## Confirmed decisions
- Offline Python processing of synchronized WAV stems; modular monolith with a CLI; no DAW plugin in M0 ([ADR-001](decisions.md)).
- Deterministic audio analysis and DSP; Claude proposes structured actions but never performs measurements or audio processing ([ADR-001](decisions.md)).
- Single agent with deterministic orchestration: application code controls the loop, validates proposals, executes DSP and verifies results ([ADR-004](decisions.md)).
- uv-managed environment, Python 3.11 ([ADR-002](decisions.md)).

## Target pipeline (planned)
Audio I/O -> deterministic features -> detectors -> structured problem candidates -> Claude proposal -> action validator -> DSP execution -> verification -> accept/revert -> experiment report.

## Implemented (M0)
M0 implements only Audio I/O -> features -> descriptive JSON report. Do not claim masking detection from overlap measures alone.

| Module | Responsibility |
| --- | --- |
| `mixing_agent.audio.io` | Load WAV stems as float64 `(frames, channels)`; reject non-WAV, unreadable, too-short (< 2048 frames), > 2-channel and non-finite input; require equal sample rate and frame count for a pair. |
| `mixing_agent.audio.features` | Mono fold-down, RMS/peak dBFS, STFT magnitudes, band-power and temporal-coactivity proxies. |
| `mixing_agent.audio.analysis` | `analyze_pair`: combines the above into the `m0.1` report dict, including input SHA-256 hashes. |
| `mixing_agent.cli` | `mixing-agent analyze`: writes the JSON report; validation errors exit with code 2 and a one-line message. |
| `scripts/generate_test_audio.py` | Deterministic synthetic kick/bass stems for smoke tests (not perceptual ground truth). |

Analysis parameters (STFT 2048/512, 30–200 Hz band, 10 % coactivity threshold) are fixed in code. `configs/analysis.yaml` documents them as a proposed manifest but is **not read** by the code yet.
