#!/usr/bin/env python3
"""Generate registry.json for the OtoDock community skills catalog.

Walks every `<package>/manifest.json`, validates the skill-package invariants
(the same ones the platform's installer enforces — catch violations in CI
before an install ever sees them), and emits a top-level `registry.json`
consumed by the OtoDock platform's Browse Community Skills UI.

Usage:
    python scripts/generate-registry.py            # write registry.json
    python scripts/generate-registry.py --check    # exit non-zero if stale

The script is intentionally dependency-free so CI doesn't need a venv.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "registry.json"
REGISTRY_VERSION = "1"
PLATFORM_MIN_VERSION = "1.2.0"

REQUIRED_MANIFEST_FIELDS = ("name", "label", "description", "version",
                            "category", "server")
# Mirrors proxy/services/mcp/mcp_manifest_types.py — skill ids become
# filesystem path components at materialization.
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_ID_MAX_LEN = 64
VALID_LOADING = {"always", "on_demand"}


def _iter_package_dirs() -> list[Path]:
    dirs = []
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name in {"scripts", "docs"}:
            continue
        if (entry / "manifest.json").is_file():
            dirs.append(entry)
    return dirs


def _manifest_hash(manifest: dict) -> str:
    """Stable hash of a manifest, ignoring the two fields the platform pins
    locally on install (`version` + `server.source`).

    CONTRACT — must stay byte-identical to the platform's
    ``proxy/services/community/community_catalog.normalized_manifest_hash``:
    the platform compares this against the same hash of each install's
    manifest to detect integration changes ("re-converge this package"). The
    serialization is pinned (`sort_keys`, compact `separators`,
    `ensure_ascii=True`) so contributor formatting doesn't affect the hash.
    """
    m = copy.deepcopy(manifest)
    m.pop("version", None)
    server = m.get("server")
    if isinstance(server, dict):
        server.pop("source", None)
    blob = json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _read_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON ({exc})")


def _frontmatter(md: str) -> dict[str, str]:
    """Best-effort flat parse of `key: value` lines in a SKILL.md frontmatter
    block (dependency-free; enough to validate name/description presence)."""
    if not md.startswith("---"):
        return {}
    end = md.find("\n---", 3)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in md[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


def _validate(manifest: dict, pkg_dir: Path) -> None:
    """Skill-package invariants. Mirrors the platform installer's
    `_validate_skill_package` (plus catalog-only requirements like README.md)
    — a package that passes here must never be rejected at install time."""
    missing = [f for f in REQUIRED_MANIFEST_FIELDS if not manifest.get(f)]
    if missing:
        raise SystemExit(f"{pkg_dir.name}: missing required fields {missing}")
    if manifest["category"] != "skill":
        raise SystemExit(
            f"{pkg_dir.name}: category must be 'skill', got {manifest['category']!r}")
    server = manifest.get("server") or {}
    if server.get("runtime") != "none" or server.get("transport") != "none":
        raise SystemExit(
            f"{pkg_dir.name}: skill packages must declare server.runtime and "
            f"server.transport as 'none'")
    if manifest["name"] != pkg_dir.name:
        raise SystemExit(
            f"{pkg_dir.name}: manifest name {manifest['name']!r} must equal "
            f"the folder name")

    skills = manifest.get("skills") or []
    if not skills:
        raise SystemExit(f"{pkg_dir.name}: skill packages must declare at "
                         f"least one skill")
    for sk in skills:
        sid = sk.get("id", "")
        if not SKILL_ID_RE.fullmatch(sid or "") or len(sid) > SKILL_ID_MAX_LEN:
            raise SystemExit(f"{pkg_dir.name}: invalid skill id {sid!r}")
        loading = sk.get("loading", "on_demand")
        if loading not in VALID_LOADING:
            raise SystemExit(
                f"{pkg_dir.name}: skill {sid}: loading must be one of "
                f"{sorted(VALID_LOADING)}, got {loading!r}")
        rel = sk.get("file", "")
        f = (pkg_dir / rel) if rel else None
        if f is None or not f.is_file() or ".." in Path(rel).parts:
            raise SystemExit(
                f"{pkg_dir.name}: skill {sid}: file {rel!r} not found in package")
        if f.name == "SKILL.md":
            fm = _frontmatter(f.read_text(encoding="utf-8"))
            if fm.get("name") != sid:
                raise SystemExit(
                    f"{pkg_dir.name}: {rel}: frontmatter name "
                    f"{fm.get('name')!r} must equal the skill id {sid!r}")
            if not fm.get("description"):
                raise SystemExit(
                    f"{pkg_dir.name}: {rel}: frontmatter description is "
                    f"required — it is the CLI's activation trigger")

    if any(p.is_file() for p in pkg_dir.rglob(".env")):
        raise SystemExit(f"{pkg_dir.name}: package must not contain .env files")
    if not (pkg_dir / "README.md").is_file():
        raise SystemExit(f"{pkg_dir.name}: README.md missing")


def _has_scripts(pkg_dir: Path) -> bool:
    """Executable content (any non-empty ``scripts/`` dir) is ALLOWED since
    2026-08-27 (platform 1.5) and surfaced as a per-entry ``has_scripts``
    badge — review script-bearing contributions extra carefully (pinned
    deps, no fetch-and-exec, no credential access; see CONTRIBUTING.md)."""
    return any(sub.is_dir() and any(sub.iterdir())
               for sub in pkg_dir.rglob("scripts"))


def _directory_size(path: Path) -> int:
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git"}]
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                pass
    return total


def _derive_tags(manifest: dict) -> list[str]:
    tags = set(manifest.get("tags", []))
    for token in manifest.get("label", "").lower().split():
        if token.isalpha() and len(token) > 2:
            tags.add(token)
    tags.add("skill")
    return sorted(tags)


def _entry_for_package(pkg_dir: Path) -> dict:
    manifest = _read_manifest(pkg_dir / "manifest.json")
    _validate(manifest, pkg_dir)
    has_icon = (pkg_dir / "icon.png").is_file()
    has_scripts = _has_scripts(pkg_dir)
    # Scripts-bearing packages need a platform that accepts them (the pre-1.5
    # installer rejected non-empty scripts/) — force the floor so older
    # platforms show "incompatible" instead of a failing install.
    def _ver(v: str) -> tuple:
        try:
            return tuple(int(x) for x in str(v).split("."))
        except ValueError:
            return (0,)
    min_version = manifest.get("platform_min_version", PLATFORM_MIN_VERSION)
    if has_scripts and _ver(min_version) < (1, 5, 0):
        min_version = "1.5.0"
    return {
        "name": manifest["name"],
        "label": manifest["label"],
        "description": manifest["description"],
        "category": "skill",
        "version": manifest["version"],
        "runtime": "none",
        "source": "",
        "version_constraint": "",
        # Hash of the package manifest (minus the locally-pinned
        # version+source); lets the platform detect catalog changes and
        # re-converge installs.
        "manifest_hash": _manifest_hash(manifest),
        "manifest_url": f"./{pkg_dir.name}/manifest.json",
        "readme_url": f"./{pkg_dir.name}/README.md",
        "icon_url": f"./{pkg_dir.name}/icon.png" if has_icon else None,
        "tags": _derive_tags(manifest),
        "author": manifest.get("author", "OtoDock"),
        "author_url": manifest.get("author_url", "https://github.com/OtoDock"),
        "license": manifest.get("license", "Apache-2.0"),
        "requires_credentials": False,
        "requires_system_packages": [],
        "has_scripts": has_scripts,
        "platform_min_version": min_version,
        "assignment_mode": manifest.get("assignment_mode", "auto"),
        "size_bytes": _directory_size(pkg_dir),
        "deprecated": bool(manifest.get("deprecated", False)),
        "patched": bool(manifest.get("patched", False)),
        "patch_note": manifest.get("patch_note"),
    }


def _build_registry() -> dict:
    skills = [_entry_for_package(d) for d in _iter_package_dirs()]
    seen_ids: dict[str, str] = {}
    for d in _iter_package_dirs():
        manifest = _read_manifest(d / "manifest.json")
        for sk in manifest.get("skills") or []:
            sid = sk.get("id", "")
            if sid in seen_ids:
                raise SystemExit(
                    f"skill id {sid!r} declared by both {seen_ids[sid]!r} and "
                    f"{d.name!r} — the skill namespace is flat")
            seen_ids[sid] = d.name
    return {
        "registry_version": REGISTRY_VERSION,
        "updated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "platform_min_version": PLATFORM_MIN_VERSION,
        "skills": skills,
    }


def _write(registry: dict, path: Path) -> None:
    text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if registry.json is stale instead of writing.",
    )
    args = parser.parse_args()

    registry = _build_registry()

    if args.check:
        if not REGISTRY_PATH.is_file():
            print("registry.json missing", file=sys.stderr)
            return 1
        existing = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        # Ignore updated_at when comparing — only structural diffs matter.
        existing.pop("updated_at", None)
        candidate = {**registry}
        candidate.pop("updated_at", None)
        if existing != candidate:
            print("registry.json is stale — run scripts/generate-registry.py",
                  file=sys.stderr)
            return 1
        print(f"registry.json is up to date ({len(registry['skills'])} skill packages)")
        return 0

    _write(registry, REGISTRY_PATH)
    print(f"Wrote {REGISTRY_PATH.relative_to(REPO_ROOT)} "
          f"({len(registry['skills'])} skill packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
