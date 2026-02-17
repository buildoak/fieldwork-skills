# fieldwork-skills Agent Installation Guide

`fieldwork-skills` is a collection of AI agent skills by buildoak. Each skill lives in `skills/<skillname>/` and includes a `SKILL.md` runbook plus update metadata.

## Critical Runtime Rules

- Codex CLI reads instructions from the repository root `AGENTS.md` only.
- Codex CLI does not read `codex.md` and does not read `.codex/skills/`.
- Claude Code reads skills from `.claude/skills/<skillname>/SKILL.md`.

## List Available Skills

Skills are the folders inside `skills/`.

```bash
ls -1 skills/
```

Current skills:
- `agent-mux`
- `browser-ops`
- `chatgpt-search`
- `google-workspace-ops`
- `gsd-coordinator`
- `image-gen`
- `summarize`
- `vault`
- `web-search`

## Install One Skill

Replace `<skillname>` with a folder name from `skills/`.

Claude Code:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R skills/<skillname> /path/to/your-project/.claude/skills/<skillname>
```

Codex CLI (append this skill's instructions to the target project's root `AGENTS.md`):

```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:<skillname> -->"
  cat skills/<skillname>/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Install All Skills

Claude Code:

```bash
mkdir -p /path/to/your-project/.claude/skills
for d in skills/*/; do
  cp -R "$d" "/path/to/your-project/.claude/skills/$(basename "$d")"
done
```

Codex CLI (append all skill runbooks into the target project's root `AGENTS.md`):

```bash
touch /path/to/your-project/AGENTS.md
for f in skills/*/SKILL.md; do
  skill="$(basename "$(dirname "$f")")"
  {
    echo
    echo "<!-- fieldwork-skill:${skill} -->"
    cat "$f"
  } >> /path/to/your-project/AGENTS.md
done
```

## Install Runtime Dependencies

After copying skill folders, read each skill's `SKILL.md` for runtime dependency setup. Skills may require brew packages, pip packages, npm packages, API keys, or other prerequisites. Each `SKILL.md` has a "Setup" section with the specific instructions. For a detailed walkthrough, see `references/installation-guide.md` inside each skill directory.

## Check for Updates

Each skill includes `UPDATES.md` describing:
- `new-files`
- `changed-files`
- `removed-files`
- `breaking-changes`
- `migration-notes`

Read `skills/<skillname>/UPDATES.md` before applying updates.

## Update Safely

Each skill includes `UPDATE-GUIDE.md` with customization-safe update steps.

Update rules:
- Never overwrite customized files without a diff and confirmation.
- Never auto-apply breaking changes.
- Never replace the entire skill folder blindly.
- Follow the skill's `UPDATE-GUIDE.md` process.
