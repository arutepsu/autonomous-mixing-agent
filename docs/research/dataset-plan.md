# Dataset and Controlled Project Plan — v1

## Source
Primary: original self-created multitrack projects with aligned WAV stem exports. DAW: FL Studio for composing/exporting; Python operates on stems.

## Candidate size (planning only)
- Calibration: 6 projects (2 per genre family).
- Held-out evaluation: 9 projects (3 per genre family).
- These are provisional targets, not a statistical sample-size justification.

## Genre families
House/techno; trap/phonk/wave; drum & bass.

## Recommended variants
For each relevant project: clean/reference condition where defensible, controlled defect variant with parameterized modification, and optional manual correction reference. Preserve all injection parameters and random seeds.

## Required manifest fields (proposal)
`project_id`, `genre_family`, `split`, `sample_rate`, `stem_files`, `track_roles`, `time_alignment`, `variant_id`, `defect_generation`, `producer_intent`, `license_or_ownership`, `notes`.

## Leakage prevention
Partition by underlying musical project, not by rendered variant: all variants from a source project must remain in the same split. Freeze detector thresholds and acceptance criteria before final evaluation.

## Validity risks
Injected faults are not automatically real-world mixing problems. Ask whether each example is actually perceptually relevant; do not claim expert ground truth without independent listening/annotation.

## Open questions
- Human listening or expert ratings as reference labels?
- Which defect intensities can be reproducibly created without trivial solutions?
- How to ensure clips are loudness-matched for perceptual comparisons?
