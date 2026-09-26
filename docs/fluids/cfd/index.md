---
title: CFD
status: working
tags: [pillar-3, pillar-4, fluids, cfd]
updated: 2026-09-26
---

# CFD

<span class="status status-working">working</span>
<span class="pillar">pillars 3, 4 &middot; Discretization, solvers</span>

The machinery that turns the [governing equations](../governing-equations.md) into numbers:
how the domain is divided, how fluxes are built, and how the resulting system is advanced.

!!! abstract "The pipeline, and where each stage goes wrong"
    - **Mesh** — quality metrics decide accuracy before a single equation is solved.
    - **Discretize in space** — face fluxes, reconstruction, limiters.
    - **Discretize in time** — stability limits, or an implicit solve.
    - **Solve the linear system** — conditioning, driven largely by mesh anisotropy.
    - **Verify** — grid convergence and manufactured solutions, before believing anything.

## Pages in this section

| Page | Covers |
|---|---|
| [Finite volume](finite-volume.md) | Integral form, face reconstruction, limiters, gradients, non-orthogonal correction |
| [Time integration](time-integration.md) | Explicit and implicit schemes, CFL and diffusive limits, stiffness, dual time stepping |
| [Meshing and grid quality](meshing.md) | Quality metrics, boundary-layer sizing, \(y^+\) targets, AMR, grid convergence |

## The recurring theme

Three of the most expensive mistakes in CFD are not errors of theory but of
**attribution** — a symptom blamed on the wrong stage:

- First-order upwind "fixing" an oscillation, when the oscillation was a mesh or
  boundedness problem and the fix replaced it with numerical diffusion thousands of times
  the physical viscosity.
- Multigrid convergence collapsing, blamed on the solver, caused by boundary-layer cell
  aspect ratio.
- A grid study on a wall-function mesh, where refinement changes the turbulence modelling
  rather than the discretization error.

Each is recorded in the failure-modes block of the relevant page.

## Connections

- [Governing equations](../governing-equations.md) · [Incompressible](../incompressible.md) · [Compressible](../compressible.md)
- [Turbulence](../turbulence/index.md) — what gets modelled rather than resolved.
- [Computing › HPC](../../computing/index.md) — running all this at scale.
