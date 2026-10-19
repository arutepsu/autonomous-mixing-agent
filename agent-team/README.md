# Using the thesis agent team

Five roles: mixing-coordinator, mixing-engineer, mixing-dsp, mixing-evaluator and thesis-supporter. The main chat normally acts as coordinator; the coordinator subagent is optional for a separate planning review.

## Configuration locations

Codex: .codex/agents/*.toml.
Claude Code: .claude/agents/*.md.
Shared project evidence and rules: agent-team/PROJECT_BRIEF.md.

Model overrides are intentionally omitted: use the parent/client settings. No permissions are broadened. Role prompts alone do not enforce a read-only sandbox. No agents are automatically started by these files.

Open the project folder in the chosen client and ask it to identify the available role definitions. If discovery fails after adding a new agents directory, start a fresh session. Native role loading depends on the installed client. If the current Codex tool cannot select custom agent types, have the coordinator read the matching TOML developer_instructions and pass those explicitly when delegating.

## First assignment

Use mixing-engineer and mixing-evaluator as specialist subagents. Read CLAUDE.md, agent-team/PROJECT_BRIEF.md (implementation baseline, thesis invariants and remaining research conflicts) and the referenced documents. Research only, within the offline Python/WAV workflow: mixing-engineer maps the current M0 implementation against the M0 exit criteria in docs/project/requirements.md; mixing-evaluator independently reviews whether those criteria and their verification methods are sufficient. Do not implement or alter project files. Wait for both, consolidate evidence and unresolved decisions, and propose the next bounded task. FL Studio integration is deferred and not part of this assignment.

## Daily workflow

1. Give the coordinator a goal and scope: research, implementation, review or writing.
2. Specify files that may change and concrete acceptance criteria.
3. Run independent investigations together; sequence dependent implementation.
4. Review evidence and decide unresolved research questions.
5. Save accepted decisions and task handoffs in ordinary project files, following CLAUDE.md (new ADRs in docs/decisions/, append-only docs/research/research-log.md).

Do not have Codex and Claude edit the same files simultaneously. Separate sessions share files, not automatic live memory or task control. These agents are development assistants: they help develop the thesis and are not the runtime mixing system, its decision_agent or a controller under evaluation (ADR-004 is unaffected). Implementation follows the offline Python/WAV baseline (ADR-001, ADR-009); FL Studio integration is deferred and optional.

## Prompt to give Claude Code

Open this project folder. Read CLAUDE.md and agent-team/PROJECT_BRIEF.md, then inspect the five existing .claude/agents/*.md definitions. Verify their format against your installed Claude Code version; preserve the role responsibilities and source boundaries. Do not overwrite existing definitions blindly or edit reference documents. If agents are not discoverable, explain how to reload them. Do not start a team or implement the mixing system yet. Report which roles are available and any missing source access. Keep Codex and Claude role meanings aligned; document any platform-specific changes.

## Format references

- Codex: https://learn.chatgpt.com/docs/agent-configuration/subagents
- Claude Code: https://code.claude.com/docs/en/sub-agents

Verification covers file structure and matching prompts. Client discovery and actual delegation must be checked separately; generated files do not prove runtime activation.
