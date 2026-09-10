<!-- Thanks for the pull request. One package per PR. CONTRIBUTING.md has the folder layout, the manifest reference, the content policy and the review checklist this list mirrors. -->

## Package

<!-- Which skill package, new or updated, and what changes. For an update: the version bump and why; for vendored content, the upstream commit. -->

## How it was tested

<!-- The OtoDock version you installed it on, and a task where an agent loaded the skill and followed it. -->

## Checklist

- [ ] `python scripts/generate-registry.py --check` passes and `registry.json` is committed.
- [ ] The skill body is instruction and reference content: nothing asks the agent to fetch and execute remote content, exfiltrate data or bypass approvals.
- [ ] The `description` is an activation trigger, scoped to the tasks the skill is for.
- [ ] Vendored content: the licence permits redistribution, `LICENSE.txt` sits in the skill folder, the upstream commit is pinned in `manifest.json` and the README records the source and every modification.
- [ ] Scripts, if any: pinned dependencies or the standard library only, no download-and-execute, no credential access, no network beyond the skill's purpose, and a README note on what they do.
- [ ] No overlap with an existing catalog skill's trigger space.
- [ ] No `.env` file, key or credential anywhere in the package.
- [ ] I have reviewed every line I submit, generated or not.
