---
title: Adaptive mesh refinement
status: working
tags: [pillar-6, computing, mesh, parallelism, performance]
updated: 2026-10-24
---

# Adaptive mesh refinement

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - AMR buys resolution where it matters by **not** paying for it elsewhere. The saving is dramatic and it is entirely determined by **what fraction of the domain the fine levels cover**.
    - **Block-structured** AMR — nested rectangular patches — keeps the inner loops dense and vectorisable, which is why it dominates GPU-era codes.
    - **Subcycling in time** multiplies the saving: coarse levels take coarse steps. It also introduces most of the complexity.
    - **Conservation at coarse–fine boundaries is not automatic.** Refluxing is what makes it conservative, and omitting it produces slow, plausible drift.
    - The hard part in production is not the refinement, it is **load balance** as the grid changes under a fixed set of ranks.

## Key results

### Flavours

| Type | Structure | Strength | Cost |
|---|---|---|---|
| **Block-structured (patch) AMR** | Nested logically rectangular grids | Dense kernels, excellent on GPUs | Refines more than strictly needed |
| **Octree / cell-based** | Each cell refines independently | Tight fit to the feature | Indirect addressing, poorer locality |
| **Unstructured adaptive** | Insert and remove elements | Complex geometry | Expensive remeshing, poor vectorisation |
| **Moving mesh (r-adaptive)** | Fixed count, moved nodes | No hanging nodes | Tangles; limited dynamic range |

Block-structured AMR is the Berger–Oliger–Colella lineage and underlies AMReX, Chombo and the codes built on them. The key property is that each patch is a dense array, so the compute kernel is the same one a uniform-grid code would use — and that is exactly what a GPU wants.

### Where the saving comes from

With refinement ratio \(r\), \(L\) levels, and each level covering a fraction \(f\) of the volume of the one below:

<div class="result" markdown>

\[
N_{\text{AMR}} = N_0 \sum_{\ell=0}^{L-1} f^{\ell} r^{d\ell},
\qquad
N_{\text{uniform}} = N_0\, r^{d(L-1)}
\]

</div>

and with subcycling the work gains another factor of \(r^{\ell}\) per level, because level \(\ell\) takes \(r^{\ell}\) steps for each coarse step. The worked example puts numbers on this; the headline is that the saving is governed by \(f\), and a feature that spreads out destroys the advantage.

### Coarse–fine boundaries

This is where the correctness lives.

- **Ghost cells** at a fine patch's edge are interpolated from the coarse level. The interpolation must preserve whatever the scheme needs — conservation, monotonicity, and for MHD or incompressible flow, the divergence constraint.
- **Refluxing.** The coarse cell adjacent to a fine patch computed its flux with coarse data; the fine cells computed a different, better flux across the same face. Without correcting the coarse cell by the difference, mass and momentum are not conserved. The error is small per step and accumulates.
- **Divergence-free prolongation.** For [MHD](../astrophysics/mhd.md) and for projected incompressible schemes, generic interpolation introduces \(\nabla\cdot\mathbf{B} \ne 0\) or a velocity field that is not discretely divergence-free. Specialised face-centred interpolation is required.
- **Proper nesting.** A fine level must be surrounded by a buffer of the next-coarser level, so that stencils never reach across two refinement jumps.

### Refinement criteria

The criterion decides everything about whether AMR pays:

| Criterion | Behaviour |
|---|---|
| Gradient or curvature of a field | Simple; **chases noise**, and refines shocks everywhere they are |
| Physics-specific tagging (vorticity, \(\lambda_2\), species, fire front) | Usually the practical choice |
| Richardson extrapolation error estimate | Principled, costs an extra coarse solve |
| Adjoint / goal-oriented | Refines what affects the output functional; the most efficient and least used |

Two practical additions: **buffer zones** of a few cells so a feature does not escape its patch between regrids, and **regrid interval** tuned so the feature cannot cross the buffer within it.

### Parallel considerations

The grid changes under a fixed rank count, so **load balance is dynamic**. Standard practice is a space-filling curve (Morton or Hilbert) over the boxes, which preserves locality while distributing work, with re-distribution at each regrid. Costs that dominate in practice: the regrid itself, data movement on redistribution, and the fact that different levels have different amounts of work per step, so subcycling creates idle time unless levels are balanced independently.

On GPUs, patch size is a tuning parameter with real consequences: boxes too small leave the device underoccupied and pay kernel-launch overhead per box; boxes too large refine volume you did not need. Many codes keep a minimum box size of 16–32 cells per side for this reason.

## Mental model

AMR is a bet that the solution is interesting in a small part of the domain. The bet pays in proportion to how small that part is, and the whole machinery — tagging, nesting, refluxing, load balance — is the price of placing it.

The second idea is that AMR changes the *shape* of the cost, not just its size. A uniform grid is one dense kernel over one array, perfectly predictable. An AMR run is many kernels over many boxes at several resolutions with irregular communication and a grid that moves. That is why AMR codes are harder to profile, harder to load-balance and harder to make deterministic — and why the performance question is usually about overheads rather than about floating-point work.

## Numerics / practice

- **Measure \(f\) in your actual runs**, not in the idealised picture. If the fine level ends up covering 40% of the domain, AMR is buying little and costing complexity.
- **Verify conservation explicitly** with refluxing on and off. The difference is the diagnostic, and if the two agree the refluxing is not wired up.
- **Test the refinement criterion on a known solution** before trusting it on a new one. Gradient tagging on a noisy field refines the noise.
- **Convergence-test with the refinement pattern held fixed**, otherwise the grid changes between runs and the convergence rate is meaningless.
- **Profile the regrid separately.** It is often a surprising fraction of the run, and regridding less often is usually free accuracy.
- **Check that the physics is level-independent.** A closure or source term with a grid-dependent parameter — an LES subgrid model, an actuator-line \(\varepsilon\) — now takes different values on different levels, which is a physics inconsistency, not a numerical one.

??? warning "Failure modes"
    **Refluxing omitted.** Conservation fails by a small amount per coarse–fine face per step. Nothing crashes; totals drift slowly, and on a long run the drift is attributed to physics.

    **Grid-dependent physics across levels.** An LES subgrid model, an [actuator-line kernel width](../aerospace/actuator-line.md), or any parameter tied to \(\Delta\) takes a different value on each level, so the model being solved differs by region. This is one of the genuinely hard problems in combining AMR with turbulence modelling, and it has no clean general answer.

    **Convergence study with adaptive tagging active.** Refining the base grid changes where the tags fire, so successive runs use different refinement patterns and the observed order of accuracy is meaningless. Freeze the pattern.

    **Gradient-based tagging on a noisy or under-resolved field.** It refines the noise, the refined region grows, \(f\) rises and the run slows until the advantage is gone — a failure that presents as a performance problem rather than a correctness one.

    **Fine level not properly nested.** Stencils reach across two levels, interpolation becomes ill-defined, and the symptom is a localised artefact at the patch corner that looks like a physics instability.

    **Load imbalance after regrid.** Rank occupancy changes with the grid. A run that was balanced at start-up can be badly imbalanced an hour in, and the usual symptom is throughput decaying over the run.

    **Divergence constraint broken by prolongation.** In MHD or incompressible flow, generic interpolation at a coarse–fine boundary introduces a constraint violation that then propagates. Needs constraint-preserving interpolation, not a cleanup pass afterwards.

    <!-- Add your own here. -->

## Worked example

What AMR actually buys, and what it depends on:

```python
import numpy as np

# Block-structured AMR: L levels, refinement ratio r, each level covering fraction f
# of the volume of the level below it. 3D, with subcycling in time (r steps per level).
def counts(N0, L, r, f, dim=3):
    cells = [N0**dim * (f**(l) ) * (r**(dim*l)) for l in range(L)]   # cells on each level
    steps = [r**l for l in range(L)]                                 # subcycles per level
    return cells, steps

print("cost of L-level AMR vs a uniform grid at the SAME finest resolution")
print(f"{'levels':>7}{'uniform cells':>16}{'AMR cells':>13}{'cell ratio':>12}"
      f"{'work ratio':>12}")
N0, r, f = 64, 2, 0.125                 # base 64^3, factor-2 refinement, 1/8 volume each level
for L in (1, 2, 3, 4, 5, 6):
    c, s = counts(N0, L, r, f)
    uni_cells = (N0 * r**(L-1))**3
    uni_work  = uni_cells * r**(L-1)                 # uniform grid must take the finest dt
    amr_work  = sum(ci*si for ci, si in zip(c, s))
    print(f"{L:7d}{uni_cells:16,.0f}{sum(c):13,.0f}{uni_cells/sum(c):12.1f}"
          f"{uni_work/amr_work:12.1f}")

print("\nthe saving depends entirely on f, the volume fraction each level covers:")
print(f"{'f':>7}{'cell ratio at L=4':>20}{'work ratio at L=4':>20}")
for f in (0.5, 0.25, 0.125, 0.0625, 0.03):
    c, s = counts(N0, 4, r, f)
    uni_cells = (N0*r**3)**3
    print(f"{f:7.3f}{uni_cells/sum(c):20.1f}{uni_cells*r**3/sum(ci*si for ci,si in zip(c,s)):20.1f}")
print("\nf -> 1 means the fine level covers everything and AMR buys nothing.")
```

```
cost of L-level AMR vs a uniform grid at the SAME finest resolution
 levels   uniform cells    AMR cells  cell ratio  work ratio
      1         262,144      262,144         1.0         1.0
      2       2,097,152      524,288         4.0         5.3
      3      16,777,216      786,432        21.3        36.6
      4     134,217,728    1,048,576       128.0       273.1
      5   1,073,741,824    1,310,720       819.2      2114.1
      6   8,589,934,592    1,572,864      5461.3     16644.1

the saving depends entirely on f, the volume fraction each level covers:
      f   cell ratio at L=4   work ratio at L=4
  0.500                 6.0                 7.0
  0.250                34.1                48.2
  0.125               128.0               273.1
  0.062               273.1              1024.0
  0.030               390.4              2249.3

f -> 1 means the fine level covers everything and AMR buys nothing.
```

The first table is the case for the method. Four levels of factor-2 refinement from a \(64^3\) base gives the same finest resolution as a uniform \(512^3\) grid, at **1/128 of the cells** — and, once subcycling is included so coarse levels take coarse time steps, **1/273 of the work**. At six levels it is a factor of 16,000. These are the numbers that make exascale atmospheric and astrophysical codes possible at all; a uniform grid at the finest resolution is simply not affordable.

The second table is the condition attached. Everything depends on \(f\), the volume fraction each level covers. At \(f = 1/8\) — each level occupying an eighth of its parent, which is one octant, a reasonable figure for a localised feature — four levels give a factor of 273 in work. At \(f = 1/2\) the same four levels give a factor of **7**. The method has not changed; the solution has.

That is the question to ask before adopting AMR: *what fraction of my domain is interesting?* A detached shock, a flame front, a fire perimeter, a single rotor in a large domain — all small \(f\), all excellent cases. Fully developed turbulence filling the domain is large \(f\), and there AMR adds complexity for a single-digit return.

The model assumes a clean nesting hierarchy and ignores regrid cost, ghost exchange and load imbalance, all of which eat into the ideal figure — typically bringing a nominal 273 down to something nearer 50–100 in production. The scaling with \(f\) survives those overheads unchanged.

## Connections

- [HPC](hpc.md) — parallel decomposition and scaling, where load balance bites.
- [GPU and CUDA](gpu-cuda.md) — why dense patches suit accelerators.
- [CFD › Meshing](../fluids/cfd/meshing.md) — grid quality and refinement criteria.
- [CFD › Time integration](../fluids/cfd/time-integration.md) — subcycling and stability across levels.
- [Astrophysics › MHD](../astrophysics/mhd.md) — divergence-free prolongation.
- [Meteorology › Multiscale coupling](../meteorology/multiscale-coupling.md) — AMR as the alternative to nesting separate models.

## Sources

- Berger & Oliger, "Adaptive mesh refinement for hyperbolic partial differential equations", *JCP* **53** (1984).
- Berger & Colella, "Local adaptive mesh refinement for shock hydrodynamics", *JCP* **82** (1989) — refluxing.
- Zhang et al., "AMReX: a framework for block-structured adaptive mesh refinement", *J. Open Source Software* **4** (2019).
- Almgren, Lattanzi, Haque, Jha, et al., "ERF: Energy Research and Forecasting", *J. Open Source Software* **8** (2023) 5202.
- Dubey et al., "A survey of high level frameworks in block-structured adaptive mesh refinement packages", *JPDC* **74** (2014).
