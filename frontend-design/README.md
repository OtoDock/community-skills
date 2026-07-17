# Frontend Design

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `frontend-design` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

Turns an agent into an opinionated design lead: instead of the safe, templated defaults LLM-built pages tend toward, it pushes for a deliberate aesthetic point of view — grounded in the subject matter, with real typography and palette decisions and one justified aesthetic risk per brief.

Pairs well with OtoDock's interactive artifacts and mini-apps: enable it for agents that build dashboards, landing pages, or `display_ui` artifacts.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `frontend-design` | Visual design guidance for building new UI or reshaping an existing one: aesthetic direction, typography, palette, layout. Use when a page, artifact, or app needs a deliberate, non-templated look. |

## Source & license

Vendored from [anthropics/skills](https://github.com/anthropics/skills) at commit
[`9d2f1ae`](https://github.com/anthropics/skills/tree/9d2f1ae187231d8199c64b5b762e1bdf2244733d/skills/frontend-design), path `skills/frontend-design`. © Anthropic,
licensed under Apache-2.0 — see `skills/frontend-design/LICENSE.txt`.
Modifications: none.
