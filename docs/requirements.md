# Requirements — v1

Status: **planned** unless stated as M0 implemented. Requirements labeled `target` may be deferred if the core experiment is at risk.

| ID | Requirement | Priority | Status |
| --- | --- | --- | --- |
| FR-01 | Load mono/stereo WAV stems | must | M0 implemented (WAV/WAVEX/RF64 containers; tested) |
| FR-02 | Validate compatible input sample rate, length, and alignment assumptions | must | M0 partial: equal sample rate and frame count, ≥ 2048 frames, ≤ 2 channels, finite samples (tested); time alignment/offset is assumed, not checked |
| FR-03 | Report RMS, peak and descriptive frequency features | must | M0 partial: RMS and peak implemented; only one frequency feature (30–200 Hz band-power proxy) is reported; feature functions lack direct numeric tests |
| FR-04 | Analyze kick/bass time-frequency interaction | must | M0 exploratory proxy only |
| FR-05 | Produce typed, uncertainty-aware problem candidates | must | planned |
| FR-06 | Request structured action proposals via Claude | must | planned |
| FR-07 | Reject unapproved actions and out-of-range parameters | must | planned |
| FR-08 | Apply bounded gain and EQ actions | must | planned |
| FR-09 | Re-analyze candidate audio and compare to previous version | must | planned |
| FR-10 | Accept, revert or stop using declared criteria | must | planned |
| FR-11 | Enforce producer intent and protected tracks | must | planned |
| FR-12 | Persist reproducible experiment records | must | M0 partial: JSON with input SHA-256 and STFT/band parameters; missing coactivity threshold, channel count, bit depth, package/Python versions |
| FR-13 | Cover resonance and stereo/phase cases | target | planned |
| FR-14 | Direct FL Studio `.flp` integration | optional | excluded from core |

## Quality constraints
- QR-01: no modification of input WAVs.
- QR-02: deterministic calculations are locally testable without model/network.
- QR-03: include input identifiers/hashes, processing config and code/model versions in experiments.
- QR-04: bounded iteration count, API usage, tool parameters and execution time.
- QR-05: tested failure behavior for corrupt/unsupported/unaligned stems.
- QR-06: no unsupported claims that energy overlap automatically implies audible masking.

## M0 exit criteria
- CLI reads valid kick/bass WAVs and saves structured JSON.
- Rejects incompatible inputs with understandable messages.
- Synthetic regression tests pass.
- Values are documented as descriptive measurements, not validated defect detection.

Status 2026-10-14: criteria 1–4 are met (17 tests pass; see `research-log.md`). The roadmap exit condition "reproducible feature report" additionally requires the FR-12 metadata gaps above to be closed.

## Open questions
- Sample-rate policy: reject vs resample (decide before datasets are built). M0 currently rejects mismatches as an interim default.
- Alignment policy and permissible offset tolerances.
- Reference-level / loudness-matching rule for correction comparisons.
