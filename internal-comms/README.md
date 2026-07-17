# Internal Comms

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `internal-comms` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

Gives an agent the house formats for common internal communications — 3P updates, status reports, leadership updates, newsletters, FAQ responses, incident reports — each with a worked example of structure and tone. The agent picks the right format for the ask instead of inventing one.

Useful for assistant-style agents that draft recurring updates from meeting notes, task history, or project state.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `internal-comms` | Formats and examples for writing internal communications: status reports, leadership updates, 3P (progress/plans/problems) updates, company newsletters, FAQs, incident reports. Use whenever asked to write internal comms. |

## Source & license

Vendored from [anthropics/skills](https://github.com/anthropics/skills) at commit
[`9d2f1ae`](https://github.com/anthropics/skills/tree/9d2f1ae187231d8199c64b5b762e1bdf2244733d/skills/internal-comms), path `skills/internal-comms`. © Anthropic,
licensed under Apache-2.0 — see `skills/internal-comms/LICENSE.txt`.
Modifications: none.
