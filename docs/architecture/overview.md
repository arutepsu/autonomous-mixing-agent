# Architecture

## Confirmed decisions
- Offline Python processing of synchronized WAV stems; modular monolith with a CLI; no DAW plugin in M0 ([ADR-001](../decisions/0001-offline-python-workflow.md)).
- Deterministic audio analysis and DSP; Claude proposes structured actions but never performs measurements or audio processing ([ADR-001](../decisions/0001-offline-python-workflow.md)).
- Single agent with deterministic orchestration: application code controls the loop, validates proposals, executes DSP and verifies results ([ADR-004](../decisions/0004-single-agent-deterministic-orchestration.md)).
- uv-managed environment, Python 3.11 ([ADR-002](../decisions/0002-uv-dependency-management.md)).
- Track-role-agnostic design: stems carry declared roles; components must not assume specific instruments such as kick/bass. Problem-specific components are added only in their roadmap phase; analysis parameters and thresholds must be configurable and documented ([ADR-006](../decisions/0006-research-first-development-policy.md)).

## Target pipeline (planned)
Audio I/O -> deterministic features -> detectors -> structured problem candidates -> Claude proposal (`decision_agent`) -> action validator -> DSP execution -> verification -> accept/revert -> experiment report.

Hidden-reference boundary ([ADR-010](../decisions/0010-hidden-reference-boundary.md), requirements SR-10): everything up to accept/revert is runtime and never reads the original reference audio or defect-injection ground truth. Run records hold runtime inputs and the action history. Research evaluation joins them with the separately stored hidden evaluation data only after execution.

## Implemented (M0)
M0 implements only Audio I/O -> features -> descriptive JSON report. Do not claim masking detection from overlap measures alone.

| Module | Responsibility |
| --- | --- |
| `autonomous_mixing.audio.io` | Load WAV stems as float64 `(frames, channels)`; reject non-WAV, unreadable, too-short (< 2048 frames), > 2-channel and non-finite input; require equal sample rate and frame count for a pair. |
| `autonomous_mixing.audio.features` | Mono fold-down, RMS/peak dBFS, STFT magnitudes, band-power and temporal-coactivity proxies. |
| `autonomous_mixing.audio.analysis` | `analyze_pair`: combines the above into the `m0.1` report dict, including input SHA-256 hashes. |
| `autonomous_mixing.cli` | `autonomous-mixing analyze`: writes the JSON report; validation errors exit with code 2 and a one-line message. |
| `scripts/generate_test_audio.py` | Deterministic synthetic kick/bass stems, formerly used for manual smoke runs (not perceptual ground truth). No test depends on it; under review per ADR-006. |

Analysis parameters (STFT 2048/512, 30–200 Hz band, 10 % coactivity threshold) are fixed in code. `configs/analysis.yaml` documents them as a proposed manifest but is **not read** by the code yet.

**Known deviations from ADR-006 (M0):** the two inputs are named `kick`/`bass` in the CLI, `analyze_pair` and the report keys, and the parameters above are hardcoded. Retained unchanged until reviewed; do not extend this pattern.

## Open questions
- How should the M0 two-stem interface generalize to role-declared stems (e.g. via the `track_roles` manifest field in [`dataset-plan.md`](../research/dataset-plan.md)), and which report-schema version change does that imply?
- Should `scripts/generate_test_audio.py` be removed or retained (and if retained, for which documented purpose)? Requires owner approval.
