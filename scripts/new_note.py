#!/usr/bin/env python3
"""Scaffold a note page from the site template.

    python3 scripts/new_note.py fluids/compressible --title "Compressible flow" --pillar 1

Writes docs/<path>.md with front matter, the standard eight-part template and today's
date. The page still has to be added to nav: in mkdocs.yml by hand — the navigation is
explicit so that section ordering stays a deliberate choice.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"

PILLARS = {
    1: "Physical modeling and domain theory",
    2: "Mathematical methods",
    3: "Discretization and numerical analysis",
    4: "Solvers, time integration and adjoints",
    5: "Programming and software engineering",
    6: "HPC and parallelism",
    7: "Domain codes and toolchains",
    8: "Data management, statistics and UQ",
    9: "Scientific machine learning",
    10: "V&V, research craft and communication",
}

TEMPLATE = """---
title: {title}
status: {status}
tags: [pillar-{pillar}{extra_tags}]
updated: {today}
---

# {title}

<span class="status status-{status}">{status}</span>
<span class="pillar">pillar {pillar} &middot; {pillar_name}</span>

!!! abstract "In one minute"
    - <!-- The irreducible core. Five bullets, no more. -->
    -
    -
    -
    -

## Key results

<!-- Equations, symbols defined, final forms boxed. Derivations only where the
     derivation is itself the insight. -->

## Mental model

<!-- The physical or geometric picture. Why the mathematics looks like this. -->

## Numerics / practice

<!-- Discretization, stability limits, conditioning, typical resolutions, cost. -->

??? warning "Failure modes"
    <!-- MANDATORY. What goes wrong, the symptom, the cause. This is the highest-value
         section on the page and the hardest to reconstruct later. Do not ship the page
         without it. -->

## Worked example

<!-- Link a notebook, or inline a snippet under twenty lines that actually runs. -->

## Connections

<!-- Sibling pages. Where this has come up in real work. -->

## Sources

<!-- Archive paths relative to the archive root, e.g. Aerospace/AERSP425/Notes/ch4.pdf
     Then books, papers, lecture series. -->
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="page path under docs/, without .md — e.g. fluids/compressible")
    ap.add_argument("--title", required=True, help="page title")
    ap.add_argument("--pillar", type=int, required=True, choices=sorted(PILLARS),
                    help="primary Skills Map pillar (1-10)")
    ap.add_argument("--tags", default="", help="comma-separated topic tags")
    ap.add_argument("--status", default="seed", choices=("seed", "working", "solid"))
    ap.add_argument("--force", action="store_true", help="overwrite an existing page")
    args = ap.parse_args(argv)

    target = DOCS / (args.path.removesuffix(".md") + ".md")

    # Refuse to clobber written work: losing a filled-in page to a mistyped path is
    # exactly the kind of error this script should not make possible.
    if target.exists() and not args.force:
        print(f"error: {target} already exists (use --force to overwrite)", file=sys.stderr)
        return 1

    if DOCS not in target.resolve().parents:
        print(f"error: {target} is outside docs/", file=sys.stderr)
        return 1

    extra = "".join(", " + t.strip() for t in args.tags.split(",") if t.strip())

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE.format(
        title=args.title,
        status=args.status,
        pillar=args.pillar,
        pillar_name=PILLARS[args.pillar],
        extra_tags=extra,
        today=dt.date.today().isoformat(),
    ), encoding="utf-8")

    rel = target.relative_to(DOCS.parent)
    print(f"wrote {rel}")
    print(f"next: add '{args.path.removesuffix('.md')}.md' to nav: in mkdocs.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
