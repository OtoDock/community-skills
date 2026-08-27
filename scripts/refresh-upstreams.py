#!/usr/bin/env python3
"""Refresh vendored skill packages from their upstream repositories.

Each package manifest records its provenance:

    "upstream": {
        "repo": "https://github.com/anthropics/skills",
        "commit": "<sha the content was vendored from>",
        "path": "skills/theme-factory",
        "exclude": ["agents/"],          // optional: upstream paths never vendored
        "frozen": true                    // optional: upstream dead/deprecated — skip
    }

This tool makes the manual re-vendor a one-command, REVIEWED operation.
The platform deliberately never auto-pulls from upstreams — curation
review and the per-refresh license re-check are the catalog's security
boundary; once a refresh is committed and published, the fleet converges
to it via the platforms' weekly auto-update.

Usage:
    python scripts/refresh-upstreams.py --check            # report drift
    python scripts/refresh-upstreams.py --apply [PKG ...]  # stage updates

``--apply`` replaces each package's vendored skill tree with the upstream
default-branch HEAD content (minus ``exclude`` entries), updates
``upstream.commit``, bumps the manifest PATCH version when content
actually changed (version is what triggers installed platforms to
re-converge — the manifest hash ignores skill-file content), and
regenerates ``registry.json``. Afterwards: review the diff, re-check the
upstream LICENSE still permits redistribution, update the package README's
provenance note, then commit.

Dependency-free (stdlib only), like generate-registry.py.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

UA = {"User-Agent": "otodock-community-skills-refresh"}


def _http_get(url: str, accept: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={**UA, **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 — fixed github hosts
        return resp.read()


def _repo_slug(repo_url: str) -> str:
    """https://github.com/owner/repo[/...] → owner/repo."""
    parts = repo_url.rstrip("/").split("github.com/", 1)
    if len(parts) != 2 or "/" not in parts[1]:
        raise SystemExit(f"unsupported upstream repo url: {repo_url}")
    owner_repo = "/".join(parts[1].split("/")[:2])
    return owner_repo


def _head_sha(repo_url: str) -> str:
    slug = _repo_slug(repo_url)
    data = _http_get(f"https://api.github.com/repos/{slug}/commits/HEAD",
                     accept="application/vnd.github.sha")
    sha = data.decode("ascii").strip()
    if len(sha) < 7:
        raise SystemExit(f"{slug}: could not resolve HEAD sha")
    return sha


def _fetch_subtree(repo_url: str, sha: str, sub_path: str, dest: Path) -> Path:
    """Download the repo tarball at ``sha`` and extract ``sub_path`` into
    ``dest``. Returns the extracted subtree root."""
    slug = _repo_slug(repo_url)
    blob = _http_get(f"https://codeload.github.com/{slug}/tar.gz/{sha}")
    out = dest / "upstream"
    prefix = None
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for member in tf.getmembers():
            if prefix is None:
                prefix = member.name.split("/", 1)[0]
            rel = member.name.split("/", 1)[1] if "/" in member.name else ""
            if not rel.startswith(sub_path.rstrip("/") + "/") and rel != sub_path.rstrip("/"):
                continue
            if member.issym() or member.islnk():
                continue  # never vendor links
            target_rel = rel[len(sub_path.rstrip("/")):].lstrip("/")
            target = out / target_rel
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                f = tf.extractfile(member)
                if f is not None:
                    target.write_bytes(f.read())
    if not out.exists():
        raise SystemExit(f"{slug}@{sha[:7]}: path {sub_path!r} not found upstream")
    return out


def _excluded(rel: str, excludes: list[str]) -> bool:
    return any(rel == e.rstrip("/") or rel.startswith(e.rstrip("/") + "/")
               for e in excludes)


def _tree_files(root: Path, excludes: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if _excluded(rel, excludes):
            continue
        out[rel] = p
    return out


def _diff(vendored: Path, upstream: Path, excludes: list[str]) -> dict:
    ours = _tree_files(vendored, excludes) if vendored.exists() else {}
    theirs = _tree_files(upstream, excludes)
    added = sorted(set(theirs) - set(ours))
    removed = sorted(set(ours) - set(theirs))
    changed = sorted(
        rel for rel in set(ours) & set(theirs)
        if ours[rel].read_bytes() != theirs[rel].read_bytes()
    )
    return {"added": added, "removed": removed, "changed": changed}


def _bump_patch(version: str) -> str:
    parts = version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        return version + ".1"
    return ".".join(parts)


def _iter_packages(names: list[str]) -> list[Path]:
    dirs = []
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in {"scripts", "docs"}:
            continue
        if not (entry / "manifest.json").is_file():
            continue
        if names and entry.name not in names:
            continue
        dirs.append(entry)
    if names:
        missing = set(names) - {d.name for d in dirs}
        if missing:
            raise SystemExit(f"unknown package(s): {', '.join(sorted(missing))}")
    return dirs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true",
                      help="Report drift vs upstream HEAD; change nothing.")
    mode.add_argument("--apply", action="store_true",
                      help="Stage upstream HEAD content into the packages.")
    parser.add_argument("packages", nargs="*",
                        help="Package folder names (default: all with an upstream).")
    args = parser.parse_args()

    drift = 0
    applied = 0
    for pkg_dir in _iter_packages(args.packages):
        manifest = json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
        upstream = manifest.get("upstream") or {}
        if not upstream.get("repo") or not upstream.get("path"):
            print(f"{pkg_dir.name}: no upstream recorded — skipped")
            continue
        if upstream.get("frozen"):
            print(f"{pkg_dir.name}: upstream FROZEN "
                  f"({upstream['repo']}) — skipped")
            continue

        skills = manifest.get("skills") or []
        if len(skills) != 1:
            print(f"{pkg_dir.name}: {len(skills)} skills — this tool handles "
                  f"single-skill packages only, skipped")
            continue
        vendored = (pkg_dir / skills[0]["file"]).parent
        excludes = list(upstream.get("exclude") or [])

        head = _head_sha(upstream["repo"])
        pinned = upstream.get("commit", "")
        with tempfile.TemporaryDirectory(prefix="skill-upstream-") as td:
            sub = _fetch_subtree(upstream["repo"], head, upstream["path"], Path(td))
            d = _diff(vendored, sub, excludes)
            dirty = bool(d["added"] or d["removed"] or d["changed"])

            tag = "up to date" if (head == pinned and not dirty) else (
                "content drift" if dirty else "commit moved, content identical")
            print(f"{pkg_dir.name}: pinned {pinned[:7] or '(none)'} → HEAD "
                  f"{head[:7]} — {tag}")
            for kind in ("added", "changed", "removed"):
                for rel in d[kind]:
                    print(f"    {kind[0].upper()} {rel}")
            if dirty or head != pinned:
                drift += 1

            if args.apply and (dirty or head != pinned):
                if dirty:
                    if vendored.exists():
                        shutil.rmtree(vendored)
                    vendored.mkdir(parents=True, exist_ok=True)
                    for rel, src in _tree_files(sub, excludes).items():
                        dst = vendored / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_bytes(src.read_bytes())
                    manifest["version"] = _bump_patch(manifest.get("version", "1.0.0"))
                manifest["upstream"]["commit"] = head
                (pkg_dir / "manifest.json").write_text(
                    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
                applied += 1
                print(f"    → applied ({'content + ' if dirty else ''}commit pin"
                      f"{', version ' + manifest['version'] if dirty else ''})")

    if args.apply and applied:
        import subprocess
        subprocess.run([sys.executable,
                        str(REPO_ROOT / "scripts" / "generate-registry.py")],
                       check=True)
        print(f"\n{applied} package(s) refreshed. Now: review the diff, "
              f"re-check each upstream LICENSE, update README provenance "
              f"notes, and commit.")
    elif args.check:
        print(f"\n{drift} package(s) with drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
