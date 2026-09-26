---
title: Large eddy simulation
status: solid
tags: [pillar-1, fluids, turbulence, les, subgrid]
updated: 2026-09-26
---

# Large eddy simulation

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - LES resolves the energetic, geometry-dependent eddies and models only the small scales, which are closer to universal. That is the entire justification.
    - The **subgrid stress** needs a model; almost all of them are eddy-viscosity models acting as a drain of energy to the unresolved scales.
    - In practice the **grid is the filter**, which makes the model resolution-dependent and the formalism less clean than it looks.
    - **Near-wall cost is the binding constraint**: wall-resolved LES scales roughly \(\mathrm{Re}^{1.8}\). Wall modelling is what makes high-\(\mathrm{Re}\) LES affordable.
    - Under-resolved LES is not conservative — it is neither LES nor RANS, and it has no error bar.

## Key results

**Filtering.** Convolve with a filter of width \(\Delta\), \(\overline{u}_i = G_\Delta * u_i\):

<div class="result" markdown>

\[
\frac{\partial \overline{u}_i}{\partial t}
+ \frac{\partial (\overline{u}_i\overline{u}_j)}{\partial x_j}
= -\frac{1}{\rho}\frac{\partial \overline{p}}{\partial x_i}
+ \nu\nabla^2\overline{u}_i
- \frac{\partial \tau_{ij}^{\mathrm{sgs}}}{\partial x_j}
\]

with the subgrid stress \(\tau_{ij}^{\mathrm{sgs}} = \overline{u_iu_j} - \overline{u}_i\overline{u}_j\).

</div>

Formally identical to RANS — but the modelled part is small and, at sufficient resolution, nearly universal, whereas in RANS it is everything.

**Smagorinsky:**

\[
\tau_{ij}^{\mathrm{sgs}} - \tfrac{1}{3}\tau_{kk}\delta_{ij} = -2\nu_t \overline{S}_{ij},
\qquad
\nu_t = (C_s\Delta)^2 |\overline{S}|,
\qquad
|\overline{S}| = \sqrt{2\overline{S}_{ij}\overline{S}_{ij}}
\]

\(C_s \approx 0.17\) for isotropic turbulence, but \(0.1\) is typical in shear flow — the constant is not universal, which is the model's central weakness.

**Dynamic procedure** (Germano). Apply a second, coarser test filter \(\widehat{\Delta} = 2\Delta\) and use the resolved stresses between the two to compute \(C_s\) locally:

\[
C_s^2 = \frac{\langle L_{ij}M_{ij}\rangle}{\langle M_{ij}M_{ij}\rangle},
\qquad
L_{ij} = \widehat{\overline{u}_i\overline{u}_j} - \widehat{\overline{u}}_i\widehat{\overline{u}}_j
\]

No tuning, correct near-wall and laminar limits, and it permits backscatter — at the price of needing averaging over homogeneous directions or Lagrangian paths to stay stable.

**WALE** recovers the correct \(\nu_t \sim y^3\) wall asymptotics without a test filter or damping function, which makes it a good default on complex geometry.

**Resolution requirements:**

| Region | Requirement |
|---|---|
| Free shear | resolve ~80% of TKE; \(\Delta \sim L/10\) |
| Wall-resolved | \(\Delta x^+ \approx 50\), \(\Delta z^+ \approx 20\), \(y^+_1 < 1\) |
| Wall-modelled | first cell in the log layer; wall stress from a model |

The near-wall numbers are in **wall units**, so they tighten as \(\mathrm{Re}\) grows — that is where the \(\mathrm{Re}^{1.8}\) comes from.

## Mental model

The cascade is a conveyor belt carrying energy from large scales to small. LES cuts the belt partway along and asks the subgrid model to do one job well: **remove energy at the right rate**. Getting the local stress tensor exactly right matters much less than getting the mean drain right — which is why crude eddy-viscosity models work at all, and why a model that occasionally drains too little blows up while one that drains too much merely looks laminar.

## Numerics / practice

- **Low-dissipation schemes are mandatory.** Central or low-dissipation upwind. A second-order upwind scheme's numerical dissipation typically exceeds the subgrid model's, in which case you are running an accidental ILES with an unknown effective filter.
- **Check the resolved fraction.** Compare modelled to resolved TKE; below ~80% resolved, the "LES" label is not earned.
- **Inflow turbulence matters.** A steady inlet profile needs a long development length before real turbulence appears. Use synthetic turbulence generation or a recycling plane, and verify the spectra downstream.
- **Average long, in homogeneous directions where they exist.** LES statistics converge no faster than the physics allows.

??? warning "Failure modes"
    **Numerical dissipation swamping the model.** With a dissipative scheme, changing \(C_s\) changes nothing — the scheme is already draining more energy than the model. Diagnostic: vary the model coefficient and watch the resolved spectrum. If it barely moves, the subgrid model is decorative.

    **Smagorinsky in transition or laminar regions.** \(\nu_t \propto |\overline{S}|\) is non-zero wherever there is mean shear, turbulent or not. In a laminar boundary layer the model adds spurious viscosity and delays or prevents transition. Fix: dynamic, WALE, or Van Driest damping.

    **Grid–filter conflation.** With the filter implicitly set by the grid, refining changes the physics being modelled, not just the discretization error. Consequence: **conventional grid convergence does not apply** — the solution should approach DNS, not a grid-independent LES. Reporting "grid-independent LES" usually means the result is dominated by numerics.

    **Commutation error.** Filtering and differentiation do not commute on non-uniform grids. Stretched meshes introduce a term nobody models, typically \(O(\Delta^2)\) but concentrated exactly where the stretching is — near walls.

    **Under-resolved LES presented as LES.** If only 40% of TKE is resolved, the model is carrying the majority of the physics, but it was calibrated to carry a minority. The result has neither LES accuracy nor RANS robustness, and no error estimate.

    **Wall-resolved cost underestimated.** \(\Delta x^+ \approx 50\) sounds generous until you convert it at \(\mathrm{Re}_L=10^7\). Always compute the cell count in wall units before committing to a mesh.

    <!-- Add your own here. -->

## Worked example

Why wall-resolved LES stops being affordable:

```python
import numpy as np

for Re in (1e5, 1e6, 1e7):
    cf    = 0.058 * Re**-0.2
    u_tau_over_U = np.sqrt(cf / 2.0)
    Re_tau = Re * u_tau_over_U           # ~ L+ , the domain in wall units
    # streamwise/spanwise spacing in wall units, boundary layer ~0.1 L thick
    nx = Re_tau / 50.0
    nz = Re_tau / 20.0
    ny = 60                              # wall-normal cells in the layer
    print(f"Re={Re:.0e}  Re_tau={Re_tau:.2e}  cells~{nx*ny*nz:.2e}")
```

```
Re=1e+05  Re_tau=5.39e+03  cells~1.74e+06
Re=1e+06  Re_tau=4.28e+04  cells~1.10e+08
Re=1e+07  Re_tau=3.40e+05  cells~6.93e+09
```

Two decades of \(\mathrm{Re}\) cost nearly four decades of cells — the \(\mathrm{Re}^{1.8}\) scaling, and the reason wall models exist.

## Connections

- [Turbulence](index.md) — scales and the cascade LES cuts into.
- [RANS](rans.md) — the alternative when only the mean is needed.
- [Time integration](../cfd/time-integration.md) — LES is inherently unsteady; CFL and time accuracy bind.

## Sources

- Pope, *Turbulent Flows*, ch. 13 — filtering and subgrid modelling.
- Germano et al. (1991) — the dynamic subgrid-scale model.
- Nicoud & Ducros (1999) — WALE.
- Archive: `Others/Turbulence_JCM`, `Others/UMD_Turb`.
