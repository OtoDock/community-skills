# OtoDock Community Skills

The catalog of **Agent Skills** ([agentskills.io](https://agentskills.io) —
`SKILL.md` folders) that an [OtoDock](https://github.com/OtoDock) instance can
install with one click. A skill teaches agents *how* to do something —
distinctive frontend design, threat modeling a repo, styling a slide deck —
as instruction and reference content the agent loads on demand when a task
matches.

This repo is the **source of truth** for what the OtoDock platform offers in
Agent Settings → Skills → Browse Community Skills. Operators don't clone it
directly — the platform pulls `registry.json` from this repo's `main` branch
and downloads individual skill packages on demand.

Skills complement [community MCPs](https://github.com/OtoDock/community-mcps):
an MCP gives agents new *tools*; a skill gives them new *technique*. A skill
package is context-only — no server process, no code execution, nothing
installed on remote machines beyond markdown and reference files.

## What's in here

```
.
├── registry.json            ← generated index, consumed by the platform UI
├── frontend-design/         ← one folder per skill package
│   ├── manifest.json        ← required: package metadata + skills[] declarations
│   ├── README.md            ← required: shown in the install dialog
│   └── skills/
│       └── frontend-design/ ← standard Agent Skills folder (folder name = skill id)
│           ├── SKILL.md     ← frontmatter (name, description) + instructions
│           ├── LICENSE.txt
│           └── (reference files the skill reads on demand)
├── scripts/
│   └── generate-registry.py ← regenerates + validates registry.json
├── CONTRIBUTING.md          ← how to add or update a skill package
└── LICENSE
```

## The seed set

Curated from the official Anthropic and OpenAI skills repositories — vendored
at a pinned upstream commit, each package's README records the exact source,
commit, license, and any modifications.

| Package | From | What it teaches |
|---|---|---|
| `frontend-design` | Anthropic | Distinctive, non-templated visual design for web UIs |
| `theme-factory` | Anthropic | 10 professional themes (+ on-the-fly generation) for slides/docs/pages |
| `algorithmic-art` | Anthropic | Generative art with p5.js — flow fields, particles, seeded randomness |
| `internal-comms` | Anthropic | House formats for status reports, 3P updates, newsletters, incident reports |
| `claude-api` | Anthropic | Building on the Claude API/SDKs — models, pricing, streaming, tools, MCP |
| `security-best-practices` | OpenAI | Language/framework-specific security reviews (Python, JS/TS, Go) |
| `security-threat-model` | OpenAI | Repository-grounded AppSec threat modeling |

## Content policy (v1)

Community skill packages carry **instruction and reference content only** —
markdown, plus inert assets (templates, fonts, PDFs). No `scripts/`
directories, no executable payloads, no `.env` files. The platform's
installer rejects violations; `scripts/generate-registry.py` enforces the
same rules in CI so a package that lands here always installs cleanly.
`SKILL.md` frontmatter is scrubbed to a declarative whitelist at install —
keys like `allowed-tools` never reach an agent session.

## License

Repository tooling and metadata: [Apache-2.0](LICENSE). Each vendored skill
keeps its own upstream license file inside its skill folder (all current
packages: Apache-2.0), with attribution in the package README.
