# ADR-002 — uv dependency management (2026-10-14)
- Decision: retain existing `pyproject.toml` and move to uv-managed environments, with `.python-version` 3.11 and committed `uv.lock` when generated.
- Rationale: easy, consistent setup and reproducible dependency resolution.
- Consequences: run commands through `uv run`; do not use `uv init` over existing project.
