# Contributing to OtoDock Community Skills

Thanks for wanting to add a skill! A skill package is **instruction and
reference content only** — it teaches agents a technique, it never runs code.
That makes contributing simpler than a community MCP, but the content rules
are stricter.

## Quick start

1. Fork this repo.
2. Create a new folder: `your-skill-name/`.
3. Put the skill folder at `your-skill-name/skills/your-skill-name/SKILL.md`
   ([Agent Skills](https://agentskills.io) format).
4. Write a `manifest.json` (schema below).
5. Write a `README.md` (what it teaches, when agents use it, source/license).
6. Run `python scripts/generate-registry.py` — it validates every package and
   refreshes `registry.json`.
7. Open a PR.

CI runs `scripts/generate-registry.py --check`. The validation is the same
the OtoDock platform's installer enforces, so a package that passes here
always installs cleanly.

## File layout — one folder per skill package

```
your-skill-name/
├── manifest.json               # required
├── README.md                   # required — shown in the install dialog
├── icon.png                    # optional, 256×256 PNG
└── skills/
    └── your-skill-name/        # folder name = skill id = frontmatter name
        ├── SKILL.md            # required — frontmatter + instructions
        ├── LICENSE.txt         # required for vendored content
        └── references, assets  # optional — markdown, templates, inert files
```

A package *may* declare several skills (several folders under `skills/`),
but one skill per package is the norm — it keeps enable/disable granular.

## `manifest.json` schema

```json
{
  "name": "your-skill-name",
  "label": "Your Skill Name",
  "description": "One-line description for catalog cards.",
  "version": "1.0.0",
  "category": "skill",
  "author": "You",
  "author_url": "https://github.com/you",
  "license": "Apache-2.0",
  "tags": ["writing"],
  "upstream": {
    "repo": "https://github.com/…",
    "commit": "<full sha the content was vendored at>",
    "path": "skills/your-skill-name"
  },
  "server": { "runtime": "none", "transport": "none" },
  "skills": [
    {
      "id": "your-skill-name",
      "loading": "on_demand",
      "file": "skills/your-skill-name/SKILL.md",
      "description": "What it does AND when to use it — this is the activation trigger.",
      "default_exclude_from": []
    }
  ]
}
```

Hard rules (enforced by `generate-registry.py` and again by the platform):

- `category` is `"skill"`, `server.runtime` and `server.transport` are
  `"none"` — a skill package is context-only, it can never gain a server
  process or code execution.
- Skill `id` = folder name = frontmatter `name`: lowercase alphanumerics and
  single hyphens, ≤64 chars. **Never rename an id after release** — installs
  key per-agent settings off it.
- `skills[].file` must exist inside the package; ids are unique across the
  whole catalog (flat namespace).
- `loading` is `"on_demand"` (default — body read only when a task matches)
  or `"always"` (inlined into every session's prompt; reserve for genuinely
  behavior-shaping content and keep it lean).
- Bump `version` on any content change; `registry.json` carries a manifest
  hash so installs re-converge automatically.

## Content policy (v1)

- **No `scripts/` directories, no executable payloads.** Skill scripts would
  run as trusted code — unsandboxed on remote machines. Until a review gate
  exists, the catalog carries instruction + reference content only.
  Inert assets (markdown, templates a skill quotes from, fonts, PDFs) are
  fine.
- **No `.env` files, keys, or credentials** anywhere in a package.
- **Frontmatter is declarative only.** `SKILL.md` frontmatter is scrubbed at
  install to `name`, `description`, `license`, `compatibility`, `metadata` —
  execution-affecting keys like `allowed-tools` are dropped. Don't rely on
  them.
- **Write the `description` as an activation trigger.** Agents' CLIs index
  the frontmatter name+description and load the body only when a task
  matches. "What it does AND when to use it", with the trigger words a user
  would actually say — not a UI label.

## Vendoring third-party skills

Vendored content must be license-compatible with redistribution (Apache-2.0,
MIT, …). Pin the exact upstream commit in `manifest.json` `upstream`, keep
the upstream `LICENSE.txt` inside the skill folder, and record source +
commit + modifications in the package README. Keep modifications minimal and
list every one.

## PR review checklist

- [ ] `generate-registry.py --check` passes
- [ ] Skill body is instruction/reference only — nothing asks the agent to
      fetch-and-execute remote content, exfiltrate data, or bypass approvals
- [ ] Description is a real activation trigger (and scoped — no "use for
      everything")
- [ ] License permits redistribution; attribution + pin recorded
- [ ] No overlap/conflict with an existing catalog skill's trigger space
