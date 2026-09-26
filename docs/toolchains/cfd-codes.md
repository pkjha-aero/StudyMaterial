---
title: CFD codes
status: seed
tags: [pillar-7, toolchains, fluids, mesh]
updated: 2026-09-26
---

# CFD codes

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotcha-lists, not tutorials. The working rule for this section: **write the entry the
    day you fight the tool**, while the workaround is still in your shell history. What is
    below is the baseline that applies to most users; the valuable entries will be yours.

## OpenFOAM

**Case structure** — the thing to internalise, because everything else is editing these:

```
case/
├── 0/                 # initial and boundary conditions, one file per field
├── constant/
│   ├── polyMesh/      # the mesh
│   └── transportProperties, turbulenceProperties
└── system/
    ├── controlDict    # time, write interval, function objects
    ├── fvSchemes      # discretization
    └── fvSolution     # linear solvers, SIMPLE/PISO controls
```

**Commands:**

```bash
blockMesh                       # generate a simple mesh
snappyHexMesh -overwrite        # mesh around STL geometry
checkMesh                       # ALWAYS run this; read the maxima
decomposePar                    # partition for parallel
mpirun -np 64 simpleFoam -parallel
reconstructPar                  # reassemble time directories
foamToVTK                       # export for ParaView
postProcess -func "sample"      # run a function object after the fact
```

**`fvSchemes` is where accuracy lives.** `div(phi,U) Gauss linear` is second-order and can
oscillate; `Gauss linearUpwind grad(U)` is the usual stable second-order choice;
`Gauss upwind` is first-order and, as [finite volume](../fluids/cfd/finite-volume.md)
explains, adds numerical diffusion that typically swamps the physical viscosity.

## ANSYS FLUENT

Journal files (`.jou`) are the reproducible interface; the GUI is for inspection. Run
`fluent 3ddp -g -t64 -i case.jou` for a batch solve. Double precision (`dp`) matters for
high aspect ratio meshes and for anything with large pressure differences.

## AMReX

Block-structured AMR framework underlying several modern codes (including
[ERF](weather-models.md)). Key concepts: `Box` (index space region), `BoxArray`,
`MultiFab` (distributed data on a BoxArray), and refinement levels with
subcycling in time. Inputs are a flat `inputs` file of `key = value` pairs.

??? warning "Failure modes"
    **`checkMesh` not run, or its output skimmed.** Maximum non-orthogonality above ~70° and skewness above ~4 will cause convergence trouble that is then blamed on schemes or relaxation. The averages are fine; it is the maxima that bite.

    **First-order upwind used to force convergence.** It always converges. See [finite volume](../fluids/cfd/finite-volume.md) — the numerical diffusion is typically thousands of times the physical viscosity, so the run is converged to a different problem.

    **`decomposePar` method mismatched to the geometry.** `simple` decomposition on a complex domain produces badly balanced, high-surface-area partitions. `scotch` is the sane default.

    **Parallel run reconstructed before it finished.** `reconstructPar` on a partially written time directory produces a corrupt field with no warning.

    **Residuals read as convergence.** OpenFOAM's initial residuals are normalised in a way that can plateau while the solution still drifts. Monitor an integral quantity — force, flow rate, a probe — as the real convergence criterion.

    **`writeInterval` set too small.** Filling the filesystem mid-run is the most common way a long job dies. Check the estimated total output before launching.

    **Single precision on a stretched mesh.** Pressure differences on high-aspect-ratio cells lose significance. Use double.

    <!-- Add your own here. -->

## Connections

- [Fluids › CFD](../fluids/cfd/index.md) — the numerics these codes implement.
- [Meshing](meshing.md) · [Visualization](visualization.md)
- [Computing › HPC](../computing/hpc.md) — running them at scale.

## Sources

- OpenFOAM User Guide and the `$FOAM_TUTORIALS` tree — the tutorials are the real documentation.
- ANSYS Fluent User's Guide; AMReX documentation.
- [Books](../resources/books.md) — Ferziger, Perić & Street for the underlying methods.
