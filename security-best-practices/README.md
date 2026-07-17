# Security Best Practices

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `security-best-practices` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

A security-review playbook: the agent identifies every language and framework in scope, then loads the matching reference sheets (Python, JavaScript/TypeScript, Go — frontend and backend) to write secure-by-default code, flag major issues, or produce a vulnerability report with suggested fixes.

Deliberately conservative triggers: it activates only when security work is explicitly requested, not on every code review.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `security-best-practices` | Language/framework-specific security best-practice reviews and secure-by-default coding guidance (Python, JavaScript/TypeScript, Go). Use when explicitly asked for a security review, security report, or secure coding help. |

## Source & license

Vendored from [openai/skills](https://github.com/openai/skills) at commit
[`49f948f`](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-best-practices), path `skills/.curated/security-best-practices`. © OpenAI,
licensed under Apache-2.0 — see `skills/security-best-practices/LICENSE.txt`.
Modifications: removed `agents/openai.yaml` (Codex plugin metadata, unused by OtoDock).
