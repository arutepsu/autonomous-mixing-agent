# Architectural decision records

One file per decision, named `NNNN-short-title.md`. Accepted ADRs are not edited; a change is a new ADR that supersedes the old one, and both are noted in this index ([ADR-003](0003-documentation-governance.md), [ADR-007](0007-docs-folder-structure.md)). File paths mentioned inside an ADR refer to the repository layout at the time it was written.

| ADR | Title | Date | Status |
| --- | --- | --- | --- |
| [001](0001-offline-python-workflow.md) | Offline Python WAV workflow, Claude for action selection, modular monolith | 2026-10-14 | Accepted |
| [002](0002-uv-dependency-management.md) | uv dependency management | 2026-10-14 | Accepted |
| [003](0003-documentation-governance.md) | Documentation governance | 2026-10-14 | Accepted; storage of ADRs refined by ADR-007 |
| [004](0004-single-agent-deterministic-orchestration.md) | Single-agent, deterministic orchestration | 2026-10-14 | Accepted |
| [005](0005-system-oriented-naming.md) | System-oriented naming | 2026-10-15 | Accepted |
| [006](0006-research-first-development-policy.md) | Research-first development policy | 2026-10-15 | Accepted |
| [007](0007-docs-folder-structure.md) | Documentation folder structure and one file per ADR | 2026-10-15 | Accepted |

## Template

```markdown
# ADR-NNN — title (YYYY-MM-DD)
- Decision:
- Source:
- Rationale:
- Consequences:
- Supersedes: (optional)
```
