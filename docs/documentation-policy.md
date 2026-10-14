# Documentation Policy

## Source-of-truth ownership
Each topic has exactly one owning document, listed in the [README documentation map](../README.md#documentation-map). Other documents link to the owner instead of repeating its content.

## Status vocabulary
Use these labels consistently so readers can tell facts from plans:
- **Confirmed decision** — recorded as an ADR in `decisions.md` (or in `project-scope.md` for research scope).
- **Implemented** — exists in code *and* is covered by a passing test; name the evidence.
- **Partial** — implemented with known gaps; name the gaps.
- **Planned** — intended, not yet implemented.
- **Open question** — unresolved research or design question; listed under "Open questions" in the owning document.
- **Assumption requiring validation** — a working parameter or premise used in code or experiments without empirical justification yet; listed in `methodology.md`.

## Allowed change types
- **Living documents** (`README.md`, scope, requirements, architecture, methodology, dataset plan, roadmap): update the appropriate section, preserving unrelated facts and indicating when prior approaches are deprecated.
- **Append-only documents** (`decisions.md`, `research-log.md`): append dated entries; do not delete or quietly replace earlier entries. Corrections are new entries referencing the prior one.
- **Outputs** (`results/`, WAVs): generated files are not documentation; keep out of Git unless intentionally curated as small public test fixtures.

## Every substantial Claude change
1. Name the requirement or experiment being changed.
2. Modify code and tests in a focused commit.
3. Update the owning living doc if behavior changed.
4. Append an ADR only for meaningful architectural decisions; append a research-log note for experiments/findings.
5. Describe tests actually run, unresolved uncertainty and affected documents.

No automatic wholesale regeneration of `.md` files.
