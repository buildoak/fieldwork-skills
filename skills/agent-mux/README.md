# agent-mux

Three problems this solves:

1. **Claude Code can't natively use Codex as a subagent.** Claude already has `Task` subagents and is a natural prompt master — it knows how to delegate. But it can't reach Codex or OpenCode out of the box. agent-mux bridges that gap: Claude dispatches Codex workers the same way it dispatches its own subagents.

2. **Codex has no subagent system at all.** No `Task` tool, no nested agents, no orchestration primitives. agent-mux gives Codex the ability to spawn workers across any engine — including Claude — through one CLI command with one JSON contract.

3. **The 10x pattern.** Inside Claude Code's `Task` subagents, you can spawn agent-mux workers. Claude architects the plan, Codex executes the code, a second Claude verifies the result — all within one coordinated pipeline. This is how `gsd-coordinator` works, and it's the same pipeline that built and audited this repo.

One CLI. One output contract. Any engine.

**Standalone project:** https://github.com/buildoak/agent-mux
For installation, usage docs, and the canonical `SKILL.md`, see the upstream repo.
