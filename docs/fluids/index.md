---
title: Fluids
status: solid
tags: [pillar-1, pillar-3, pillar-4, fluids, cfd]
---

# Fluids

<span class="status status-solid">solid</span>
<span class="pillar">pillars 1, 3, 4</span>

Continuum mechanics through to CFD practice. The richest section of the source archive, and
the section used to prove out the note template.

## Pages

| Page | Covers |
|---|---|
| [Governing equations](governing-equations.md) | Conservation laws, Navier-Stokes, nondimensionalization, regime identification |
| [Incompressible flow](incompressible.md) | Pressure as Lagrange multiplier, projection, SIMPLE/PISO, Rhie-Chow |
| [Compressible flow](compressible.md) | Characteristics, shocks, Riemann solvers, limiters |
| [Turbulence](turbulence/index.md) | Scales, cascade, spectra, and the closure problem |
| &nbsp;&nbsp;› [RANS closures](turbulence/rans.md) | Boussinesq, k-ε, k-ω SST, wall treatment and \(y^+\) |
| &nbsp;&nbsp;› [Large eddy simulation](turbulence/les.md) | Filtering, Smagorinsky, dynamic and WALE models, resolution cost |
| [CFD](cfd/index.md) | The discretization pipeline |
| &nbsp;&nbsp;› [Finite volume](cfd/finite-volume.md) | Face fluxes, reconstruction, limiters, gradients, non-orthogonality |
| &nbsp;&nbsp;› [Time integration](cfd/time-integration.md) | CFL and diffusive limits, explicit vs implicit, stiffness |
| &nbsp;&nbsp;› [Meshing and grid quality](cfd/meshing.md) | Quality metrics, boundary-layer sizing, AMR, grid convergence |

## Reading order

For a cold recap, follow the physics down into the numerics:

**[Governing equations](governing-equations.md)** → split by regime into
**[incompressible](incompressible.md)** or **[compressible](compressible.md)** →
**[turbulence](turbulence/index.md)** for what cannot be resolved →
**[CFD](cfd/index.md)** for how any of it is actually computed.

For a specific problem, go straight to the failure-modes block of the relevant page. That
is where the answer usually is.

## Sources

Archive pointers are listed per page. `Others/Jameson`, `Others/Turbulence_JCM` and
`Others/UMD_Turb` carry most of the CFD and turbulence material; see the
[course archive](../resources/course-archive.md) for the rest.
