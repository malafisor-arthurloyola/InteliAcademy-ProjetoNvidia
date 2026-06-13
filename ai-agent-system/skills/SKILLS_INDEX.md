# Skills Index

This file is the living index for project-local Codex skills used by NVIDIA Startup AI Radar.

Whenever a skill is created, downloaded, renamed, or removed under `ai-agent-system/skills`, update this index in the same change.

## Local Convention

- Skills live in `ai-agent-system/skills/<skill-name>/`.
- Each skill must have a valid `SKILL.md`.
- Prefer lowercase, hyphenated folder names.
- Keep project-specific skills aligned with `AGENTS.md` and `ai-agent-system/docs/Projeto_ NVIDIA Startup AI Radar (1).md`.

## Installed Skills

| Skill | Origin | Purpose | When to use | Status |
|---|---|---|---|---|
| `agent-architecture-audit` | GitHub: `affaan-m/ECC/skills/agent-architecture-audit` at `5b173d2e6c11b976a0f13b2f59125e08956c1d47` | Audits LLM and agent application architecture for wrapper regressions, memory pollution, tool discipline failures, hidden repair loops, and rendering corruption. | Use before releasing or deeply debugging agent/LLM features, especially multi-step workflows with tools, memory, retries, or wrappers. | Installed |
| `find-skills` | GitHub: `vercel-labs/skills/skills/find-skills` from `main` | Helps discover and install agent skills from the open skills ecosystem. | Use when looking for an existing skill for a domain, tool, workflow, framework, or repeated task. | Installed |
| `langgraph-nvidia-startup-radar` | Local project skill | Guides LangGraph architecture for the NVIDIA Startup AI Radar multiagent pipeline. | Use when designing, implementing, refactoring, testing, or documenting the Search Planner, Scraper, Extractor, Classifier, Validator, NVIDIA RAG, Recommendation, and Briefing agents. | Created locally |
| `mcp-builder` | Local copy of Codex skill | Guides creation and evaluation of MCP servers. | Use when the project needs external tools/APIs exposed through Model Context Protocol. | Installed |
| `skill-creator` | Local copy of Codex skill | Guides creation or update of Codex skills. | Use when formalizing a project workflow, domain rule, or reusable procedure as a skill. | Installed |
| `skill-installer` | Local copy of Codex skill | Installs skills from curated lists or GitHub paths. | Use when downloading skills into this project or into the Codex global skills directory. | Installed |

## Maintenance Checklist

When adding a new skill:

1. Place it under `ai-agent-system/skills/<skill-name>/`.
2. Validate it with `skill-creator/scripts/quick_validate.py` when possible.
3. Add a row to the Installed Skills table.
4. Record origin precisely: local, copied, or GitHub repo/path/ref.
5. Note any local compatibility edits, such as frontmatter cleanup.

## Local Compatibility Notes

- `agent-architecture-audit`: removed unsupported frontmatter keys (`origin`, `tools`) after download so the local validator accepts the skill.
