# agent-mux

This folder is an integration pointer for the standalone `agent-mux` project:
- https://github.com/buildoak/agent-mux

`agent-mux` provides a unified CLI for dispatching AI coding workers across Codex, Claude, and OpenCode with one JSON output contract.

Dependency note:
- `skills/gsd-coordinator` requires the upstream `agent-mux` CLI at runtime.
- This repository does not vendor the full `agent-mux` implementation.

Use `SKILL.md` in this folder for fieldwork integration guidance, and use the upstream repository for installation, flags, and canonical runtime behavior.
