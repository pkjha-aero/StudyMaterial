---
title: Astrophysics codes
status: seed
tags: [pillar-7, toolchains, flash, athena, gadget, zeus]
updated: 2026-09-26
---

# Astrophysics codes

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotchas, not tutorials. Write the entry the day you fight the tool.

## The landscape

| Code | Method | Typical use |
|---|---|---|
| FLASH | block-structured AMR, finite volume | astrophysical hydro/MHD, nuclear burning |
| Athena++ | static/adaptive mesh, high-order Godunov | MHD, accretion discs, well-documented |
| Gadget-4 | TreePM + SPH | cosmological structure formation |
| AREPO | moving Voronoi mesh | galaxy formation, Galilean-invariant |
| ZEUS-MP | finite difference, constrained transport | classic MHD; in the course archive |
| yt | analysis and visualisation | reads essentially all of the above |

## Common configuration concerns

**Units.** Every code has an internal unit system, and the conversion to CGS is set in the
configuration rather than being universal. Getting it wrong produces results that are
self-consistent and physically meaningless — and they often look plausible, because the
dynamics are scale-free in the relevant limit.

**Boundary conditions.** Periodic, outflow, reflecting, user-defined. Outflow boundaries
that permit inflow are a recurring source of unphysical mass injection.

**Refinement criteria.** AMR codes refine on a user-specified criterion — density
gradient, pressure gradient, a Jeans-length condition. The criterion matters more than the
maximum level: gradient-based refinement chases noise, and a Jeans-resolution criterion is
what prevents artificial fragmentation.

## Analysis with yt

```python
import yt
ds = yt.load("plt00100")             # FLASH, Athena, Gadget, AMReX, ...
print(ds.field_list)                 # what is actually in the file
print(ds.derived_field_list)         # what yt can compute

slc = yt.SlicePlot(ds, "z", "density")
slc.set_zlim("density", 1e-26, 1e-22)
slc.annotate_grids()                 # see the AMR structure
slc.save()

ad = ds.all_data()
print(ad.quantities.extrema("temperature"))
print(ad.quantities.total_mass())
```

`ds.derived_field_list` is the useful one — yt computes a large number of physical
quantities from the primitive fields, correctly, including unit handling.

??? warning "Failure modes"
    **Unit system misconfigured.** Internal code units converted with the wrong length or mass scale. Everything remains self-consistent, so no check inside the run catches it. Verify against an analytic scale — a free-fall time, a sound crossing time — early.

    **\(\nabla\cdot\mathbf{B}\) not monitored.** For MHD runs, track it in dimensionless form throughout. See [MHD](../astrophysics/mhd.md) — a growing divergence produces forces along field lines that look like physics.

    **Refinement criterion chasing noise.** Gradient-based refinement on a noisy field refines everywhere and the run stalls. Use a physically motivated criterion, and cap the level.

    **Artificial fragmentation from under-resolving the Jeans length.** A self-gravitating simulation that does not resolve the Jeans length by several cells fragments numerically. The clumps look like physics and are grid artefacts.

    **Softening length not reported.** N-body results depend on it, and it is frequently omitted from papers. See [N-body](../astrophysics/n-body-gravity.md).

    **Outflow boundary admitting inflow.** Mass and momentum enter from outside with no physical source. Check the global mass budget.

    **Restart files not bit-identical to the run state.** Some codes drop diagnostic or random state on restart, so a restarted run diverges from a continuous one. Test it once, deliberately, before relying on long restart chains.

    <!-- Add your own here. -->

## Connections

- [Astrophysics › MHD](../astrophysics/mhd.md) · [N-body](../astrophysics/n-body-gravity.md) · [Radiative transfer](../astrophysics/radiative-transfer.md)
- [Visualization](visualization.md) — yt and ParaView.
- Archive: `Astro/ZEUS_MP` in the [course archive](../resources/course-archive.md).

## Sources

- FLASH, Athena++, Gadget-4 and yt documentation.
- [Books](../resources/books.md) — Aarseth for N-body; Goedbloed & Poedts for MHD.
- Archive: `Astro/ZEUS_MP` in the [course archive](../resources/course-archive.md).
