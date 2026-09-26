#!/usr/bin/env python3
"""Check every page against the site's own conventions.

    python3 scripts/audit_pages.py            # report
    python3 scripts/audit_pages.py --strict   # exit 1 on any finding (for CI)

Checks the things `mkdocs build --strict` cannot: that pages declare a status and tags,
show a badge, and carry the Connections and Sources sections the note template asks for.
Also reports the status distribution, which is the honest summary of how finished the
site is, and flags pages nothing links to.

Exceptions are deliberate and listed below rather than silently tolerated:
  - meta pages (home, tags, how-to-use, skills-map) are not topic pages;
  - section index pages carry Connections but not Sources — their pages hold those;
  - the resources reference pages *are* sources, so requiring a Sources section on them
    would be circular.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

META = {"index.md", "tags.md", "how-to-use.md", "skills-map.md"}
NO_SOURCES_NEEDED = {
    "resources/books.md",
    "resources/papers.md",
    "resources/videos-playlists.md",
    "resources/courses-progress.md",
    "resources/course-archive.md",   # this page *is* the source index
}

# Reference catalogues rather than topic pages: a failure-modes block on a bibliography
# would be filler, and filler is worse than an honest exception.
NO_FAILURE_MODES_NEEDED = {
    "resources/books.md",
    "resources/papers.md",
    "resources/videos-playlists.md",
    "resources/courses-progress.md",
    "resources/course-archive.md",
}
VALID_STATUS = {"seed", "working", "solid"}


def pages() -> list[pathlib.Path]:
    return sorted(
        p for p in DOCS.rglob("*.md")
        if "snippets" not in p.parts
    )


def front_matter(text: str) -> str:
    return text.split("---")[1] if text.startswith("---") else ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if anything is flagged")
    args = ap.parse_args(argv)

    findings: list[str] = []
    status_count: collections.Counter = collections.Counter()
    all_text: dict[str, str] = {}

    for path in pages():
        rel = path.relative_to(DOCS).as_posix()
        text = path.read_text(encoding="utf-8")
        all_text[rel] = text
        fm = front_matter(text)
        is_meta = rel in META
        is_index = path.name == "index.md"

        m = re.search(r"^status:\s*(\w+)", fm, re.M)
        if not m:
            findings.append(f"{rel}: no `status` in front matter")
        elif m.group(1) not in VALID_STATUS:
            findings.append(f"{rel}: status '{m.group(1)}' not in {sorted(VALID_STATUS)}")
        else:
            status_count[m.group(1)] += 1
            if f'class="status status-{m.group(1)}"' not in text:
                findings.append(f"{rel}: status is '{m.group(1)}' but the badge does not match")

        if not re.search(r"^tags:", fm, re.M) and not is_meta:
            findings.append(f"{rel}: no `tags` in front matter")

        if "## Connections" not in text and not is_meta:
            findings.append(f"{rel}: no Connections section")

        if ("## Sources" not in text and not is_meta and not is_index
                and rel not in NO_SOURCES_NEEDED):
            findings.append(f"{rel}: no Sources section")

        # A topic page whose failure-modes block is missing has skipped the point of
        # the template. Index and meta pages are exempt.
        if (not is_meta and not is_index and "??? warning" not in text
                and rel not in NO_FAILURE_MODES_NEEDED):
            findings.append(f"{rel}: no failure-modes block")

    # Orphans: a page no other page links to is unreachable except through nav.
    for rel in all_text:
        if rel == "index.md":
            continue
        name = pathlib.Path(rel).name
        others = "".join(t for r, t in all_text.items() if r != rel)
        if name not in others:
            findings.append(f"{rel}: nothing links to this page")

    total = sum(status_count.values())
    print(f"{len(all_text)} pages   " + "  ".join(
        f"{k}={status_count[k]}" for k in ("solid", "working", "seed")) +
        f"   (statuses counted: {total})")
    print()
    if findings:
        print(f"{len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
    else:
        print("no findings — every page satisfies the site conventions")

    return 1 if (findings and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
