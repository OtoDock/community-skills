# OtoDock Community Skills

The catalog of **Agent Skills** that an [OtoDock](https://github.com/OtoDock)
instance can install with one click. An Agent Skill is a `SKILL.md` folder, as
[agentskills.io](https://agentskills.io) defines it. A skill teaches agents
*how* to do something, such as distinctive frontend design, threat modeling a
repo or styling a slide deck. It is instruction and reference content, and the
agent loads it on demand when a task matches.

This repo is the **source of truth** for what the OtoDock platform offers in
Agent Settings → Skills → Browse Community Skills. Operators don't clone it
directly. The platform pulls `registry.json` from this repo's `main` branch
and downloads individual skill packages on demand.

Skills complement [community MCPs](https://github.com/OtoDock/community-mcps).
An MCP gives agents new *tools*, and a skill gives them new *technique*. A
skill package is context-only. It has no server process and no code
execution. It installs nothing on remote machines beyond markdown and
reference files.

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

Curated from the official Anthropic and OpenAI skills repositories. Each
package is vendored at a pinned upstream commit. Its README records the exact
source, commit, license, and any modifications.

<!-- catalog:start -->
| Package | Version | From | What it teaches |
|---------|---------|------|-----------------|
| [algorithmic-art](./algorithmic-art/) | 1.0.2 | [Anthropic](https://github.com/anthropics/skills) | Generative art with p5.js — seeded randomness, flow fields, particle systems, and interactive parameter… |
| [claude-api](./claude-api/) | 1.0.1 | [Anthropic](https://github.com/anthropics/skills) | Comprehensive reference for building on the Claude API and Anthropic SDKs — model ids, pricing, streaming,… |
| [frontend-design](./frontend-design/) | 1.0.0 | [Anthropic](https://github.com/anthropics/skills) | Distinctive, intentional visual design guidance for building or reshaping web UIs — aesthetic direction,… |
| [internal-comms](./internal-comms/) | 1.0.0 | [Anthropic](https://github.com/anthropics/skills) | Formats and worked examples for internal communications: status reports, leadership updates, 3P updates,… |
| [security-best-practices](./security-best-practices/) | 1.0.0 | [OpenAI](https://github.com/openai/skills) | Language- and framework-specific security best-practice reviews and secure-by-default coding guidance for… |
| [security-threat-model](./security-threat-model/) | 1.0.0 | [OpenAI](https://github.com/openai/skills) | Repository-grounded threat modeling — trust boundaries, assets, attacker capabilities, abuse paths, and… |
| [theme-factory](./theme-factory/) | 1.0.0 | [Anthropic](https://github.com/anthropics/skills) | Ten professional color-and-font themes, plus on-the-fly theme generation, for styling slides, documents,… |
<!-- catalog:end -->

## Content policy

A skill package carries instructions and reference content: markdown, plus
inert assets (templates, fonts, PDFs). It may also carry a `scripts/`
folder, as the Agent Skills standard allows. A skill's scripts run through
the agent's normal shell tool, under the platform's permission tiers. They
are reviewed before they land here, and the registry flags such a package
(`has_scripts`), so the platform shows that it bundles scripts.

No package carries `.env` files, keys or credentials.
`scripts/generate-registry.py` checks that in CI.
[CONTRIBUTING.md](CONTRIBUTING.md) has the full policy.

`SKILL.md` frontmatter is scrubbed to a declarative whitelist at install.
Keys like `allowed-tools` never reach an agent session.

## License

Repository tooling and metadata: [Apache-2.0](LICENSE). Each vendored skill
keeps its own upstream license file inside its skill folder, with attribution
in the package README. All current packages are Apache-2.0.
