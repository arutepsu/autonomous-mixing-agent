# ADR-021 — explicit processing specification carried through execution contracts (2026-10-21)
- Status: Proposed; awaiting owner review of the implementing stage.
- Decision: represent the numerical and encoding settings of bounded offline gain/full-mix processing as an explicit, versioned domain record, carry it unchanged into processing, and require each output's evidence to record the same complete specification. No DSP or file operations are added.
  1. `domain.project.ProcessingSpec(reference: VersionRef, precision, gain_rule, summation_order, level_policy, output_container, sample_encoding)`: every field is required and type-checked, with no defaults, dictionaries, formula strings, registry or callbacks. The initial enum members and their exact meanings:
     - `NumericalPrecision.FLOAT64`: all calculations in IEEE-754 double precision.
     - `GainRule.DB_AMPLITUDE`: multiplier `10 ** (gain_db / 20)` applied to the fixed-input samples (ADR-019).
     - `SummationOrder.RECIPE_SEQUENTIAL`: a zero accumulator, then each stem added in recipe order. `MixRecipe`'s `SummingPolicy.SAMPLE_SUM` names the combination operation; `SummationOrder` names its evaluation order.
     - `LevelPolicy.PRESERVE`: no clipping, normalization, limiting or automatic level correction.
     - `OutputContainer.WAV` with `SampleEncoding.FLOAT64`: floating-point WAV with 64-bit samples, with no integer PCM conversion or dither. A later file adapter maps this encoding to its library's actual subtype; that mapping is not implemented or claimed here.
  2. Propagation: `ExecutionRequest`, `ProcessingPlan` and `ArtifactProcessingEvidence` each gain a required `processing_spec: ProcessingSpec`. `preflight_execution` carries the request's specification into the plan unchanged; rejection codes, precedence, authorization, recipe and metadata rules are unchanged. `validate_processed_candidate` additionally requires each output's evidence to record a specification equal, as a complete immutable value, to the plan's. Processor-identity agreement and render-spec checks are kept.
  3. `RenderSpec` still specifies sample rate and channel count; its fields, ownership and meaning are unchanged.
- Source: owner-approved ProcessingSpec design of 2026-10-21; audit finding F3 (pre-DSP review of 2026-10-21).
- Rationale: QR-03 requires records to carry the configuration used. Without an explicit specification, two runs citing the same processor could differ in precision, gain rule, summation order or encoding, and nothing in the records would show it.
- Consequences:
  - Intentional constructor additions to `ExecutionRequest`, `ProcessingPlan` and `ArtifactProcessingEvidence`. No global default specification is supplied.
  - Specification equality establishes recorded configuration consistency only. Evidence stays an adapter claim until the adapter is implemented and tested, and processor identity is separate from processing configuration.
  - Python, dependency and code/build versions and actual processing evidence remain required for experiment provenance (QR-03 is not met).
  - A stable operation order does not promise bitwise-identical results across every environment.
  - No global registry prevents one `VersionRef` from being reused inconsistently across separate records or runs.
  - Each enum has a single member today, so a reference-only comparison cannot be distinguished from complete-value comparison by any valid configuration; the code compares complete values.
  - F3 is narrowed, not closed: the adapter's subtype mapping and its evidence remain unimplemented. F2, F4 and F6 are unaffected.
