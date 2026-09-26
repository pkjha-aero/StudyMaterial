---
title: Meshing and grid quality
status: solid
tags: [pillar-3, fluids, cfd, meshing, amr]
updated: 2026-09-26
---

# Meshing and grid quality

<span class="status status-solid">solid</span>
<span class="pillar">pillar 3 &middot; Discretization and numerical analysis</span>

!!! abstract "In one minute"
    - Mesh quality explains more bad CFD results than scheme choice does, and it is the part most often left unreported.
    - Four numbers matter: **non-orthogonality, skewness, aspect ratio, expansion ratio**. Know the worst value of each before trusting a run.
    - The boundary layer is meshed to a **\(y^+\) target**, and the target is set by the turbulence treatment, not by the geometry.
    - High aspect ratio is necessary in boundary layers and simultaneously wrecks linear-solver conditioning. That tension is unavoidable; managing it is the craft.
    - A result without a **grid convergence study** is an anecdote. GCI is the standard way to attach a number to it.

## Key results

**Quality metrics**, with \(\mathbf{d}_{PN}\) the cell-centre vector and \(\mathbf{n}_f\) the face normal:

<div class="result" markdown>

| Metric | Definition | Target | Degrades |
|---|---|---|---|
| Non-orthogonality | \(\cos^{-1}\!\big(\hat{\mathbf{d}}_{PN}\cdot\hat{\mathbf{n}}_f\big)\) | \(< 60°\) | diffusive flux accuracy |
| Skewness | offset of face-intersection from face centre, normalised | \(< 0.85\) | convective interpolation |
| Aspect ratio | longest / shortest cell dimension | \(< 100\) (bulk) | solver conditioning |
| Expansion ratio | adjacent cell size ratio | \(< 1.2\) | truncation error, wave reflection |

</div>

**First-cell height from a \(y^+\) target.** With a flat-plate estimate \(c_f = 0.058\,\mathrm{Re}_L^{-0.2}\):

\[
u_\tau = U\sqrt{\frac{c_f}{2}},
\qquad
y_1 = \frac{y^+ \nu}{u_\tau}
\]

Place the *cell centre* at \(y_1\) — for a cell-centred code the first cell height is \(2y_1\). Getting this factor wrong is a common and quiet source of \(y^+\) being double the intent.

**Boundary-layer stack.** Growth ratio \(r\), first height \(h_1\), \(n\) layers:

\[
\delta_{\text{covered}} = h_1\frac{r^n - 1}{r - 1}
\]

Size \(n\) so the prism layer covers the whole boundary layer thickness \(\delta \approx 0.37 L\,\mathrm{Re}_L^{-1/5}\); ending the stack inside the layer puts a size jump where the gradients are steepest.

**Grid Convergence Index** (Roache), for solutions \(\phi_1\) (fine) and \(\phi_2\) (coarse), refinement ratio \(r\), observed order \(p\):

\[
\mathrm{GCI} = \frac{F_s\,|\phi_1-\phi_2|}{|\phi_1|\,(r^p - 1)}, \qquad F_s = 1.25 \text{ (three grids)}
\]

Observed \(p\) is computed from three grids; if it differs sharply from the scheme's nominal order, the meshes are not in the asymptotic range and the GCI is not meaningful.

## Mental model

A mesh is a statement about where you expect gradients. Cells should be small along the direction of rapid change and may be long along directions of slow change — which is exactly why boundary-layer cells are thin normal to the wall and long along it, at aspect ratios of \(10^3\)–\(10^4\).

The cost is conditioning. A cell 1000× longer than it is thick makes the discrete Laplacian strongly anisotropic, and isotropic smoothers (Jacobi, point Gauss–Seidel, standard multigrid coarsening) lose their effectiveness in exactly that region. The fix is to make the solver anisotropy-aware — line relaxation or semi-coarsening along the stretched direction — rather than to fix the mesh.

## Numerics / practice

- **Mesh to the physics, not to the geometry.** Refine wakes, shear layers and shocks; a uniformly fine mesh wastes cells where nothing happens.
- **Check \(y^+\) after solving.** It depends on the converged \(u_\tau\); the pre-mesh estimate is only a starting guess, often out by a factor of two.
- **Keep the expansion ratio low across interfaces**, especially prism-to-tet. That transition is where quality collapses on most hybrid meshes.
- **AMR** helps where the feature moves (shocks, flame fronts, interfaces); the refinement criterion matters more than the machinery. Gradient-based criteria chase noise — prefer an error estimator or a physics-specific indicator.

??? warning "Failure modes"
    **First cell in the buffer layer.** \(5 < y^+ < 30\) is valid for neither wall functions nor wall-resolved modelling. The usual cause is meshing from a \(y^+\) estimate and never checking the realised value.

    **Prism stack ending inside the boundary layer.** A sudden prism-to-tet jump where velocity gradients are still steep. Symptom: a kink in the velocity profile at a fixed distance from the wall, immovable under refinement, and wall heat flux that will not converge.

    **High aspect ratio blamed on the solver.** Multigrid convergence collapsing in the boundary layer is a mesh-anisotropy problem showing up in the solver. Adding iterations does not help; semi-coarsening or line-implicit smoothing does.

    **Rapid cell-size jumps.** Expansion ratios above ~1.3 reflect acoustic and vortical content back into the domain and raise truncation error locally. Symptom in LES or aeroacoustics: spurious reflections from an interior mesh interface, which look like physics.

    **Refining a wall-function mesh.** Refinement moves \(y^+\) down into the buffer layer, so the solution changes for modelling reasons, not discretization ones. The grid study then measures the wrong thing entirely. Either refine away from the wall only, or convert to wall-resolved.

    **GCI computed outside the asymptotic range.** Three grids too coarse, or too close in refinement ratio, give an observed order far from nominal and an uncertainty estimate with no meaning. Use \(r \ge 1.3\) and check the observed order.

    **Trusting an automatic mesh report.** Most generators report averages. It is the worst cell that destabilises the run — always look at maxima and at *where* the bad cells are.

    <!-- Add your own here. -->

## Worked example

Sizing a prism stack to actually cover the boundary layer:

```python
import numpy as np

U, L, nu = 50.0, 2.0, 1.5e-5
Re = U * L / nu
delta  = 0.37 * L * Re**-0.2                    # turbulent BL thickness
cf     = 0.058 * Re**-0.2
u_tau  = U * np.sqrt(cf / 2.0)
h1     = 2.0 * (1.0 * nu / u_tau)               # cell height for y+ = 1 at centre

for r in (1.1, 1.2, 1.3):
    n = int(np.ceil(np.log(1 + delta * (r - 1) / h1) / np.log(r)))
    print(f"growth {r}:  {n:2d} layers to cover delta = {delta*1e3:.1f} mm")
```

```
growth 1.1:  56 layers to cover delta = 31.9 mm
growth 1.2:  33 layers to cover delta = 31.9 mm
growth 1.3:  25 layers to cover delta = 31.9 mm
```

The usual default of 10–15 prism layers does not reach the edge of the boundary layer at this Reynolds number — the stack ends mid-layer, exactly the failure mode above.

## Connections

- [Finite volume](finite-volume.md) — non-orthogonality and skewness corrections.
- [RANS closures](../turbulence/rans.md) — where the \(y^+\) target comes from.
- [LES](../turbulence/les.md) — resolution in wall units.
- [Foundations › V&V](../../foundations/index.md) — grid convergence as verification.

## Sources

- Roache, *Verification and Validation in Computational Science and Engineering* — GCI.
- Moukalled, Mangani & Darwish — mesh quality metrics and their corrections.
- Archive: see the [course archive](../../resources/course-archive.md).
