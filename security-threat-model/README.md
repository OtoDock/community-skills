# Security Threat Model

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `security-threat-model` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

Produces an AppSec-grade threat model that is specific to the repository under analysis rather than a generic checklist: trust boundaries, assets, realistic attacker capabilities, concrete abuse paths, and prioritized mitigations, every architectural claim anchored to evidence in the code. Output is a concise Markdown document following a fixed contract.

Deliberately conservative triggers: activates only on explicit threat-modeling requests, not general architecture or review work.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `security-threat-model` | Repository-grounded AppSec threat modeling: enumerate trust boundaries, assets, attacker capabilities, abuse paths, mitigations; produce a concise Markdown threat model. Use when explicitly asked to threat model a codebase or path. |

## Source & license

Vendored from [openai/skills](https://github.com/openai/skills) at commit
[`49f948f`](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-threat-model), path `skills/.curated/security-threat-model`. © OpenAI,
licensed under Apache-2.0 — see `skills/security-threat-model/LICENSE.txt`.
Modifications: removed `agents/openai.yaml` (Codex plugin metadata, unused by OtoDock).
