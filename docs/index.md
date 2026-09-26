---
title: Home
status: working
---

# Study Material

<span class="status status-working">working</span>

Recap notes in computational physics, aerospace, meteorology and machine learning.

## What this is

A **recap surface**, not a textbook.

Every page here is written for a reader who already has the skills and needs to reload a
topic quickly — the equations, the mental model, and above all the failure modes, without
the derivation chain that a textbook already owns. If you are meeting a topic for the
first time, the [sources](resources/index.md) at the foot of each page are the better
starting point.

Some sections are stable and written once: [Foundations](foundations/index.md),
[Fluids](fluids/index.md), [Aerospace](aerospace/index.md),
[Astrophysics](astrophysics/index.md). Others are active growth areas that expand
continuously: [Meteorology](meteorology/index.md), [Machine Learning](ml/index.md),
[Deep Learning](dl/index.md), [Computer Vision](cv/index.md) and
[Scientific ML](sciml/index.md).

## Where to start

<div class="grid cards" markdown>

- :material-map-outline: **[Skills Map](skills-map.md)**

    The ten competency pillars this site is organized around, with an honest
    self-assessment. The best entry point if you are browsing rather than looking
    something up.

- :material-compass-outline: **[How to use this site](how-to-use.md)**

    Page conventions, the note template, status badges and the tag taxonomy.

- :material-archive-outline: **[Course archive](resources/index.md)**

    A catalog of the external coursework archive — roughly 11 GB of notes, problem sets
    and lecture material that lives on separate storage and is indexed, not published.

- :material-magnify: **Search**

    Press <kbd>/</kbd>. Faster than the navigation for anything you can already name.

</div>

## Reading a page

Pages follow one shape, so you can skim to the part you need:

| Section | What it gives you |
|---|---|
| **In one minute** | The irreducible core. Enough to hold a conversation. |
| **Key results** | Equations, with symbols defined and final forms boxed. |
| **Mental model** | The physical or geometric picture behind the algebra. |
| **Numerics / practice** | Discretization, stability limits, typical resolutions. |
| **Failure modes** | What goes wrong, the symptom, and the cause. |
| **Worked example** | A notebook or a short snippet that runs. |
| **Connections** | Sibling topics, and where this shows up in real work. |
| **Sources** | Archive pointers, books, papers, lectures. |

The **failure modes** block is the one that earns the site. Equations are recoverable from
any textbook in ten minutes; the knowledge that a scheme goes unstable at a particular
aspect ratio, or that a dataset's fill values are silently valid-looking, is not written
down anywhere and is the first thing to decay from memory.

## Status badges

Pages are labelled honestly rather than left blank:

<span class="status status-seed">seed</span> a stub — the topic is claimed, not written ·
<span class="status status-working">working</span> usable, still being filled in ·
<span class="status status-solid">solid</span> complete enough to rely on

As of the last update the site is **31 solid, 47 working, 7 seed**. The recap sections —
foundations, fluids, aerospace, astrophysics — are written; the growth areas are marked
`working` because they will keep expanding, not because they are unfinished; the `seed`
pages are mostly [toolchains](toolchains/index.md), which are deliberately waiting for
first-hand entries.
