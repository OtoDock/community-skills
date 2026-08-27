# Algorithmic Art

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `algorithmic-art` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

A two-step creative-coding workflow: the agent first writes a short "algorithmic philosophy" — a computational aesthetic it commits to — then expresses it as p5.js generative art with seeded randomness, delivered as an interactive HTML viewer with parameter exploration. Ships two reference templates (viewer HTML + generator skeleton) the agent adapts per piece.

A great showcase for OtoDock's in-chat artifact display.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `algorithmic-art` | Creating algorithmic/generative art with p5.js: seeded randomness, flow fields, particle systems, interactive parameter exploration. Use when asked to create art with code or generative/algorithmic art. |

## Source & license

Vendored from [anthropics/skills](https://github.com/anthropics/skills) at commit
[`3b3fad9`](https://github.com/anthropics/skills/tree/3b3fad96af16a10759d930941b4520ba0c40edae/skills/algorithmic-art), path `skills/algorithmic-art`. © Anthropic,
licensed under Apache-2.0 — see `skills/algorithmic-art/LICENSE.txt`.
Modifications: none.
