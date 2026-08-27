# Skill Creator

**Agent Skill package** — instructions, reference material, and helper
scripts. Installs the `skill-creator` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

Anthropic's meta-skill for authoring skills: walks the agent through
designing a new skill, drafting its SKILL.md, packaging it, running evals
against test prompts, benchmarking versions with variance analysis, and
optimizing the description for reliable triggering. Pairs naturally with
OtoDock's skill-package zip install — users can author a skill with this and
upload the result from the admin Skills page.

**Bundles executable scripts** (`scripts/`, `eval-viewer/` — packaging,
validation, and eval-review helpers the agent runs with its normal shell
tool). Requires platform ≥ 1.5.0 (earlier installers reject script-bearing
packages).

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `skill-creator` | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, or benchmark skill performance. |

## Source & license

Vendored from [anthropics/skills](https://github.com/anthropics/skills) at commit
[`3b3fad9`](https://github.com/anthropics/skills/tree/3b3fad96af16a10759d930941b4520ba0c40edae/skills/skill-creator), path `skills/skill-creator`. © Anthropic,
licensed under Apache-2.0 — see `skills/skill-creator/LICENSE.txt`.
Modifications: appended an "OtoDock platform note" section to SKILL.md
(the install/enable flow on OtoDock; plain .zip packaging).
