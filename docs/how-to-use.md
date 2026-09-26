---
title: How to use this site
status: working
---

# How to use this site

<span class="status status-working">working</span>

Conventions, so that pages stay uniform enough to skim and the site stays useful as it
grows past the point where any one person remembers all of it.

## The note template

Every topic page has the same eight parts, in the same order. Skip to the one you need.

!!! abstract "In one minute"
    Five bullets, no more. The irreducible core of the topic — enough to hold a
    conversation, or to decide whether this is the page you actually wanted.

**Key results.** The equations, symbols defined, final forms boxed. A derivation appears
only when the derivation *is* the insight; otherwise it is a citation.

**Mental model.** The physical or geometric picture. Why the mathematics takes the shape
it does. This is the part that makes a topic reload quickly years later.

**Numerics / practice.** How it gets discretized or implemented: stability limits,
conditioning, typical resolutions, cost scaling.

??? warning "Failure modes"
    What goes wrong, what the symptom looks like, and what causes it.

    **Mandatory.** This section is the point of the site. Textbooks record how a method
    works when it works; nobody writes down that a scheme destabilizes past a given cell
    aspect ratio, or that a dataset encodes missing values as plausible numbers. That
    knowledge is expensive to acquire and the first to decay.

**Worked example.** A notebook link, or a snippet under twenty lines that actually runs.

**Connections.** Sibling pages, and where the topic has come up in real work.

**Sources.** Archive pointers, books, papers, lectures — so the page is a map into the
material rather than a replacement for it.

## Creating a page

```bash
python3 scripts/new_note.py fluids/compressible --title "Compressible flow" --pillar 1
```

This writes `docs/fluids/compressible.md` with the template, front matter and today's
date. Add the page to `nav:` in `mkdocs.yml` — the navigation is explicit on purpose, so
that section ordering is a decision rather than an alphabetical accident.

## Status badges

<span class="status status-seed">seed</span>
The topic is claimed and its sources listed; the body is not written.

<span class="status status-working">working</span>
Usable. Core results are present; failure modes or examples may be thin.

<span class="status status-solid">solid</span>
Complete enough to rely on without opening the sources.

Declared in front matter as `status:` and repeated as a badge under the page title.
Labelling a stub honestly is better than leaving it out of the navigation: a visible gap
is information.

## Tags

Two axes, both flat, both applied in front matter:

**Pillar** — `pillar-1` … `pillar-10`, from the [Skills Map](skills-map.md). Exactly one
per topic page: the primary competency it serves. Section index pages are the exception
and may carry several, since a section legitimately spans pillars.

**Topic** — free-form and cross-cutting: `turbulence`, `spectral-methods`, `pytorch`,
`netcdf`, `wrf`. As many as genuinely apply. These exist so that a topic is reachable from
more than one path — spectral methods matter to both a fluids reader and an ML reader, and
the navigation tree can only put them in one place. Browse them on the
[Tags](tags.md) page.

```yaml
---
title: Compressible flow
status: working
tags: [pillar-1, fluids, shocks, riemann]
updated: 2026-09-26
---
```

## Mathematics

LaTeX, via MathJax. Inline as `\( ... \)`, display as `\[ ... \]`.

\[
\nabla \cdot \mathbf{u} = 0,
\qquad
\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u}
= -\frac{1}{\rho}\nabla p + \nu\nabla^{2}\mathbf{u}
\]

Define every symbol on first use in a page. A page that assumes you remember its own
notation fails at exactly the moment it is needed.

## Abbreviations

Common acronyms resolve on hover automatically — CFL, RANS, MOST, NetCDF — from
`docs/snippets/abbreviations.md`, which is appended to every page at build time. Add new
ones there rather than defining a glossary per page.

## Linking to the archive

The course archive lives on external storage and is not published. Cite it by its path
relative to the archive root, so the pointer survives the drive being remounted
elsewhere:

> Source: `Aerospace/AERSP425/Notes/ch4.pdf`

The [course archive catalog](resources/index.md) resolves those paths and is searchable.

## Building locally

```bash
source ~/.venvs/studymaterial/bin/activate
mkdocs serve
```

CI builds with `--strict`, where warnings are errors — a broken internal link fails the
build rather than shipping. Run `mkdocs build --strict` before pushing.
