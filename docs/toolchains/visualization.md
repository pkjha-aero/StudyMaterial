---
title: Visualization tools
status: seed
tags: [pillar-7, toolchains, paraview, visit, yt, tecplot]
updated: 2026-09-26
---

# Visualization tools

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotchas, not tutorials. Write the entry the day you fight the tool.

## The landscape

| Tool | Strength | Scripting |
|---|---|---|
| ParaView | general, parallel, client-server on HPC | `pvpython` / `pvbatch` |
| VisIt | very large data, strong parallel record | Python |
| Tecplot | publication-quality CFD plots, engineering workflows | macros |
| yt | astrophysics, unit-aware, AMR-native | Python-first |
| Matplotlib / PyVista | scripted figures, embedding | Python |

## ParaView on a cluster

The pattern that matters: **do not copy the data to your laptop.** Run the render server
on the cluster, connect the client over a tunnel.

```bash
# on the cluster, inside a job allocation
mpirun -np 32 pvserver --server-port=11111

# on your machine
ssh -L 11111:compute-node:11111 cluster
# ParaView → File → Connect → localhost:11111
```

For batch rendering, `pvbatch script.py` runs headless and parallel — the right way to
produce a movie from a large time series.

```python
from paraview.simple import *
r = OpenDataFile("out.xmf")
sl = Slice(Input=r); sl.SliceType.Normal = [0, 0, 1]
Show(sl); ColorBy(GetDisplayProperties(sl), ("POINTS", "velocity", "Magnitude"))
GetActiveView().ViewSize = [1920, 1080]
SaveScreenshot("frame.png")
```

## Colormaps

Use perceptually uniform maps — viridis, cividis, or ParaView's *Fast*/*Viridis*. For
diverging data about a meaningful zero (vorticity, anomaly, difference), use a diverging
map with white at zero — *Cool to Warm* is the sensible default.

**Rainbow/jet is still the default in several CFD post-processors and should be changed.**
It creates false banding at the yellow-cyan transition, hides real gradients in the green
band, and is unreadable in greyscale and for colour-blind readers. See
[research craft](../foundations/research-craft.md).

## Common operations

| Task | ParaView filter |
|---|---|
| Cut plane | Slice |
| Isosurface | Contour |
| Streamlines | Stream Tracer |
| Vortex cores | Gradient → Q-criterion → Contour |
| Time average | Temporal Statistics |
| Cell → point data | Cell Data to Point Data |
| Extract a line | Plot Over Line |

??? warning "Failure modes"
    **Rainbow colormap.** Invents structure and hides gradients. The most common way a technically correct figure misleads.

    **Colour range rescaled per timestep.** The default "rescale to data range" changes the mapping every frame, so a movie shows a field that appears to pulse while the physics is steady. Lock the range.

    **Cell data interpolated to points without thinking.** Finite-volume data lives on cells; smoothing it to points for a pretty contour hides the actual discretization, including under-resolution. Fine for presentation, misleading for diagnosis.

    **Isosurface of an under-resolved field.** Contours of a field with 2–3 cells per feature produce shapes determined by the interpolation scheme. Check the mesh before believing the surface.

    **Downloading the data instead of rendering remotely.** Copying a terabyte to visualise a slice. Client-server exists for this.

    **Screenshot at the default resolution for a paper.** 400×400 px into a two-column figure. Set `ViewSize` explicitly, and render at least 2× the final size.

    **Q-criterion threshold chosen to look good.** It is not a dimensionless invariant across cases; a threshold tuned on one Reynolds number shows a different structure density at another. Normalise it, and report the value.

    <!-- Add your own here. -->

## Connections

- [CFD codes](cfd-codes.md) · [Astro codes](astro-codes.md) — the data sources.
- [Foundations › Research craft](../foundations/research-craft.md) — figures that do not mislead.
- [Fluids › Turbulence](../fluids/turbulence/index.md) — what the Q-criterion is showing.

## Sources

- ParaView Guide; VisIt manual; yt documentation.
- Crameri, Shephard & Heron (2020) on colour — see [Papers](../resources/papers.md).
