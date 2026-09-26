#!/usr/bin/env python3
"""Render the coursework index into the published catalog page.

    python3 catalog/render_catalog.py

Merges the generated index (coursework_index.yml) with the hand-maintained names and
topics (course_titles.yml) and writes docs/resources/course-archive.md.

The page lists courses, not files. It carries enough to decide whether a folder is worth
opening — what it covers, how much is there, what kinds of material — plus the path to
open it on the drive. No filenames, no instructor attribution.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent

SECTION_LINKS = {
    "aerospace": "../aerospace/index.md",
    "fluids": "../fluids/index.md",
    "astrophysics": "../astrophysics/index.md",
    "foundations": "../foundations/index.md",
    "computing": "../computing/index.md",
    "meteorology": "../meteorology/index.md",
}


def human_size(n: int) -> str:
    if n >= 2**30:
        return f"{n / 2**30:.1f} GB"
    if n >= 2**20:
        return f"{n / 2**20:.0f} MB"
    return f"{max(n // 1024, 1)} KB"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", default=str(HERE / "coursework_index.yml"))
    ap.add_argument("--titles", default=str(HERE / "course_titles.yml"))
    ap.add_argument("-o", "--out", default=str(REPO / "docs/resources/course-archive.md"))
    args = ap.parse_args(argv)

    index_path = pathlib.Path(args.index)
    if not index_path.exists():
        print(f"error: {index_path} not found — run build_catalog.py first", file=sys.stderr)
        return 2

    idx = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    titles = (yaml.safe_load(pathlib.Path(args.titles).read_text(encoding="utf-8"))
              or {}).get("courses", {}) or {}

    t = idx["totals"]
    named = sum(1 for k in _all_keys(idx) if (titles.get(k) or {}).get("name"))

    out: list[str] = []
    w = out.append

    w("---")
    w("title: Course archive")
    w("status: working")
    w("tags: [resources, archive]")
    w(f"updated: {idx['generated']}")
    w("---")
    w("")
    w("# Course archive")
    w("")
    w('<span class="status status-working">working</span>')
    w("")
    w("An index of coursework held offline. The material itself is **not** on this site "
      "and is not redistributed — this page exists so that a topic can be traced back to "
      "the course that covers it, and the folder opened on the drive.")
    w("")
    w("!!! info \"What this lists\"")
    w(f"    **{t['courses']} courses** across **{t['departments']} departments** — "
      f"{t['files']:,} files, {human_size(t['bytes'])} in total.")
    w("")
    w("    Courses, not files. Each row says what the material covers and how much of it "
      "there is; open the path on the drive for the detail. There are deliberately no "
      "filenames and no instructor attribution here.")
    w("")

    if named < t["courses"]:
        w(f"!!! warning \"{t['courses'] - named} of {t['courses']} courses are unnamed\"")
        w("    Course codes alone are enough to locate a folder, but not to know what is "
          "in it. Names and topics are filled in by hand in `catalog/course_titles.yml` "
          "— only the self-evident ones are done, because a guessed course title is "
          "worse than a visibly missing one.")
        w("")

    w("## Departments")
    w("")
    w("| Department | Courses | Files | Size | Feeds |")
    w("|---|--:|--:|--:|---|")
    for dept, info in sorted(idx["departments"].items()):
        courses = info["courses"]
        files = sum(c["files"] for c in courses.values())
        size = sum(c["bytes"] for c in courses.values())
        sec = info.get("section")
        link = f"[{sec}]({SECTION_LINKS[sec]})" if sec in SECTION_LINKS else "—"
        anchor = dept.lower().replace(" ", "-")
        w(f"| [{dept}](#{anchor}) | {len(courses)} | {files:,} | {human_size(size)} | {link} |")
    w("")

    for dept, info in sorted(idx["departments"].items()):
        w(f"## {dept}")
        w("")
        w("| Course | Covers | Extent | Material | On the drive |")
        w("|---|---|--:|---|---|")
        for key, c in sorted(info["courses"].items()):
            meta = titles.get(key) or {}
            label = c.get("code") or key
            name = meta.get("name") or ""
            covers = ", ".join(meta.get("topics") or []) or ("*" + name + "*" if name else "—")
            if name and meta.get("topics"):
                course = f"**{label}**<br>{name}"
            else:
                course = f"**{label}**"
            kinds = ", ".join(c.get("kinds") or []) or "—"
            w(f"| {course} | {covers} | {c['files']:,} files<br>{human_size(c['bytes'])} "
              f"| {kinds} | `{c['path']}` |")
        w("")

    w("## Connections")
    w("")
    w("- [Learning roadmap](courses-progress.md) — the areas this material supports.")
    w("- [Books](books.md) · [Papers](papers.md) · [Videos](videos-playlists.md)")
    w("- [How to use this site](../how-to-use.md) — how archive paths are cited on topic pages.")
    w("")
    w("---")
    w("")
    w(f"Generated from `{idx['archive_root']}` on {idx['generated']} by "
      "`catalog/build_catalog.py`. Regenerate with:")
    w("")
    w("```bash")
    w("python3 catalog/build_catalog.py && python3 catalog/render_catalog.py")
    w("```")

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {out_path.relative_to(REPO)}")
    print(f"  {t['courses']} courses, {named} named, {t['courses'] - named} to fill")
    return 0


def _all_keys(idx: dict):
    for info in idx["departments"].values():
        yield from info["courses"]


if __name__ == "__main__":
    raise SystemExit(main())
