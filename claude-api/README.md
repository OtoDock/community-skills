# Claude API

**Agent Skill package** — instruction/reference content only, no server, no
code execution. Installs the `claude-api` skill
([Agent Skills](https://agentskills.io) format), which agents load on demand
when a task matches its description.

Anthropic's own up-to-date reference for writing code against the Claude API: current model ids and pricing, request parameters, streaming, tool use, MCP connectors, agent patterns, prompt caching, batches, and migration notes — broken out per language (Python, TypeScript, Java, Go, C#, PHP, Ruby, plus raw curl) so the agent reads only the stack it's working in.

Enable it for developer agents: it stops them answering Claude API questions from stale training data.

## Contents

One skill, loaded `on_demand`:

| Skill | Description |
|---|---|
| `claude-api` | Reference for the Claude API / Anthropic SDKs: model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, migration — per-language docs for Python, TypeScript, Java, Go, C#, PHP, Ruby, curl. Use when writing or debugging code that calls Claude. |

## Source & license

Vendored from [anthropics/skills](https://github.com/anthropics/skills) at commit
[`9d2f1ae`](https://github.com/anthropics/skills/tree/9d2f1ae187231d8199c64b5b762e1bdf2244733d/skills/claude-api), path `skills/claude-api`. © Anthropic,
licensed under Apache-2.0 — see `skills/claude-api/LICENSE.txt`.
Modifications: none.
