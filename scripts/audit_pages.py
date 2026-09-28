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

# Tags are a closed vocabulary. The previous free-form scheme reached 205 tags with 177
# used exactly once, which cross-links nothing — the entire point of having tags. Adding
# one is a deliberate act: it belongs here and on docs/tags.md, and only if it will land
# on three or more pages across at least two sections.
SECTION_TAGS = {
    "aerospace", "astrophysics", "computer-vision", "computing", "deep-learning",
    "fluids", "foundations", "machine-learning", "meteorology", "resources",
    "sciml", "thermal", "toolchains",
}
CONCEPT_TAGS = {
    "boundary-layer", "conservation", "data-formats", "discretization", "extrapolation",
    "inverse-problems", "mesh", "neural-networks", "numerical-stability", "optimization",
    "parallelism", "performance", "radiation", "remote-sensing", "reproducibility",
    "scaling", "spectral-methods", "statistics", "surrogates", "turbulence",
    "uncertainty", "validation", "wildfire",
}
ALLOWED_TAGS = SECTION_TAGS | CONCEPT_TAGS


def pages() -> list[pathlib.Path]:
    return sorted(
        p for p in DOCS.rglob("*.md")
        if "snippets" not in p.parts
    )


def front_matter(text: str) -> str:
    return text.split("---")[1] if text.startswith("---") else ""


def check_notebooks(findings: list[str]) -> int:
    """Notebook cross-links must use built URLs, not .md paths.

    MkDocs rewrites `foo.md` to the built URL on ordinary pages. nbconvert does not —
    notebook markdown is converted outside that pipeline, so a `.md` link survives into
    the HTML as a dead link. `mkdocs build --strict` cannot see inside notebook output,
    so nothing else catches this.
    """
    import json

    count = 0
    for nb_path in sorted(DOCS.rglob("*.ipynb")):
        rel = nb_path.relative_to(DOCS).as_posix()
        count += 1
        try:
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"{rel}: cannot be read as a notebook ({exc})")
            continue

        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "markdown":
                continue
            text = "".join(cell.get("source", []))
            for m in re.finditer(r"\]\(([^)]+\.md)\)", text):
                findings.append(
                    f"{rel}: cell {i} links to '{m.group(1)}' — use the built URL "
                    f"(../../section/page/), nbconvert does not rewrite .md")

        # Outputs must be committed, or the site shows empty cells.
        code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
        if code_cells and not any(c.get("outputs") for c in code_cells):
            findings.append(f"{rel}: no cell outputs — commit the notebook executed")
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if anything is flagged")
    args = ap.parse_args(argv)

    findings: list[str] = []
    status_count: collections.Counter = collections.Counter()
    topic_tags: collections.Counter = collections.Counter()
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

        tag_m = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.M)
        if not tag_m and not is_meta:
            findings.append(f"{rel}: no `tags` in front matter")
        elif tag_m:
            tags = [x.strip() for x in tag_m.group(1).split(",") if x.strip()]
            for t in tags:
                if not t.startswith("pillar-"):
                    topic_tags[t] += 1
                    if t not in ALLOWED_TAGS:
                        findings.append(
                            f"{rel}: tag '{t}' is outside the controlled vocabulary")
            pillars = [t for t in tags if t.startswith("pillar-")]
            if pillars and not is_meta:
                # The primary pillar leads and must agree with the badge, or the page is
                # filed under two competencies at once.
                first = pillars[0].split("-")[1]
                badge = re.search(r'class="pillar">pillars? (\d+)', text)
                if badge and badge.group(1) != first:
                    findings.append(
                        f"{rel}: first tag is {pillars[0]} but the badge says pillar {badge.group(1)}")
            elif not pillars and not is_meta and not is_index and "resources/" not in rel:
                findings.append(f"{rel}: no pillar tag")

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

    n_notebooks = check_notebooks(findings)

    total = sum(status_count.values())
    print(f"{len(all_text)} pages, {n_notebooks} notebooks   " + "  ".join(
        f"{k}={status_count[k]}" for k in ("solid", "working", "seed")) +
        f"   (statuses counted: {total})")
    print()
    if findings:
        print(f"{len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
    else:
        print("no findings — every page satisfies the site conventions")

    # Informational, not a finding: a tag used once cross-links nothing, which is the
    # whole point of having tags. Worth watching, not worth failing a build over.
    singles = sorted(t for t, c in topic_tags.items() if c == 1)
    print(f"\n{len(topic_tags)} topic tags in use, of {len(ALLOWED_TAGS)} in the vocabulary")
    if singles:
        print(f"  used on only one page: {', '.join(singles)}")
        print("  a tag on one page cross-links nothing — retire it or apply it wider")

    return 1 if (findings and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
