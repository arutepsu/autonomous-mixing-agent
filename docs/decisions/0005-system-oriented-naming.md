# ADR-005 — system-oriented naming (2026-10-15)
- Decision: the software is named as a system, not as an agent. Repository and Python distribution `autonomous-mixing-system`; display name "Autonomous Mixing System"; import package `autonomous_mixing` (previously `mixing_agent`); CLI command `autonomous-mixing` (previously `mixing-agent`). The planned AI decision component (ADR-004) is named `decision_agent`.
- Supersedes: the naming note in `research-log.md` (2026-10-14, "repository preparation"). The thesis title is unchanged.
- Rationale: the AI agent is one component of a larger deterministic system (ADR-001, ADR-004); naming the whole project "agent" overstated its role.
- Consequences: "agent" is reserved for the decision component, the optional `agent` dependency extra and the thesis title. No behavior or report schema changes. The GitHub repository was renamed to `arutepsu/autonomous-mixing-system` (old URLs redirect).
