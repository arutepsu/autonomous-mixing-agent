# Research Scope — v1 (2026-10-14)

## Topic
Autonomous Detection and Correction of Mixing Problems Using AI Agents.

## Main research question
To what extent can an AI agent autonomously detect, correct and verify selected technical mixing problems in multitrack music using deterministic audio analysis while respecting producer intent?

## Subquestions
- RQ1: How can selected mixing problems be represented as measurable observations?
- RQ2: Can an LLM agent choose appropriate actions from measurements, context and producer intent?
- RQ3: Does iterative correction outperform an otherwise comparable one-pass approach?
- RQ4: Can validation and rollback prevent unsafe or unsuccessful interventions?

## Working hypotheses (to test, not to assume)
- H1: On controlled cases, agent-guided corrections improve predetermined technical objectives.
- H2: Re-analysis and revision increase success or reduce unresolved defects versus one pass.
- H3: Constraints and verification reduce undesirable or out-of-intent interventions.

## Problem families / priority
1. Kick/bass spectral and temporal masking (first vertical slice).
2. Frequency buildup / resonance (extension).
3. Stereo / phase compatibility (extension).

## Core boundaries
- Offline synchronized WAV stems, manually declared track roles, Python DSP.
- Claude API proposes structured actions through a validated tool interface.
- Original audio remains unchanged; each action is reversible.
- No new foundation-model training, comprehensive automatic mixing/mastering, general genre classification, guaranteed perceptual superiority, or mandatory FL Studio project integration.

## Study genres
House/techno, trap/phonk/wave, and drum & bass; genre comparisons are exploratory unless data supports them.

## Open questions
- Which published perceptual masking or multitrack-interaction methodology is feasible?
- How will defect labels and acceptance criteria be established independently?
- What is the smallest effective benchmark given creation/annotation time?
