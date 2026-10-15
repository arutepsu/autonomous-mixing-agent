# Methodological constraints
1. Synthetic test stems are not a validated psychoacoustic ground truth. Synthetic numerical signals are used only in focused unit tests of signal-processing code; generated audio is never an evaluation dataset or evidence of system performance ([ADR-006](../decisions/0006-research-first-development-policy.md)).
2. Do not call STFT overlap itself perceptual masking.
3. Avoid selecting success thresholds on final evaluation projects. Every detection threshold and analysis parameter must be documented with its source (literature or calibration split); values without one are listed below as assumptions requiring validation, not treated as established ([ADR-006](../decisions/0006-research-first-development-policy.md)).
4. Compare unprocessed, deterministic baseline, single-pass agent, iterative agent.
5. Protect raw audio, record provenance, and account for regressions and loudness side effects.

## Assumptions requiring validation
These parameters are working choices in the M0 code; none has been justified empirically or from literature yet.
- STFT frame 2048 / hop 512 samples (≈46 ms / 11.6 ms at 44.1 kHz) gives adequate time-frequency resolution for kick/bass interaction. At 44.1 kHz this leaves only 8 bins in 30–200 Hz.
- 30–200 Hz is the relevant band for kick/bass interaction across the study genres.
- A frame counts as "active" when its full-band energy exceeds 10 % of the stem's maximum frame energy; this relative threshold depends on the stem's own dynamics, not on absolute level or audibility.
- Mono fold-down (channel mean) is acceptable for low-frequency analysis; this hides inter-channel phase cancellation.
- Equal sample rate and frame count are treated as sufficient evidence of a shared timeline; sample-accurate alignment of exports is assumed, not measured.
- Synthetic stems from `scripts/generate_test_audio.py` exercise the code path only; they say nothing about perceptual relevance. The script is no longer part of the validation workflow and is under review (ADR-006).
