---
title: Finite volume method
status: solid
tags: [pillar-3, fluids, discretization, conservation]
updated: 2026-09-26
---

# Finite volume method

<span class="status status-solid">solid</span>
<span class="pillar">pillar 3 &middot; Discretization and numerical analysis</span>

!!! abstract "In one minute"
    - FV discretizes the **integral** conservation law, so conservation holds exactly per cell and globally — at machine precision, on any mesh.
    - The entire method reduces to one question: **what is the flux through each face?** Reconstruction, Riemann solvers and limiters are all answers to it.
    - **Godunov's theorem**: a linear monotone scheme is at most first order. Second order without oscillations therefore requires a *nonlinear* limiter.
    - Gradient reconstruction is where unstructured accuracy is won or lost — Green–Gauss is cheap and degrades on irregular meshes; least-squares is robust.
    - **Non-orthogonality and skewness** are the practical accuracy killers, and their corrections are explicit, which costs you convergence rate.

## Key results

**The starting point.** Integrate the conservation law over cell \(\Omega_i\) and apply the divergence theorem:

<div class="result" markdown>

\[
\frac{d}{dt}\int_{\Omega_i}\phi\,dV + \oint_{\partial\Omega_i}\mathbf{F}\cdot\mathbf{n}\,dS = \int_{\Omega_i} S\,dV
\]

\[
\Rightarrow\quad
V_i\frac{d\overline{\phi}_i}{dt} + \sum_{f} \mathbf{F}_f\cdot\mathbf{n}_f A_f = V_i \overline{S}_i
\]

</div>

A face is shared by exactly two cells, and the same flux leaves one and enters the other. Conservation is structural, not approximate — this is the property that makes FV the default for fluids.

**Face reconstruction.** For an interface value from cell-centred data:

| Scheme | Face value | Order | Behaviour |
|---|---|---|---|
| First-order upwind | \(\phi_U\) | 1 | bounded, heavily diffusive |
| Central | \(\tfrac{1}{2}(\phi_P+\phi_N)\) | 2 | oscillates when \(\mathrm{Pe}_{\text{cell}} > 2\) |
| MUSCL / linear upwind | \(\phi_U + \tfrac{1}{2}\psi(r)\nabla\phi\cdot\mathbf{d}\) | 2 | bounded if \(\psi\) is TVD |
| QUICK | 3-point quadratic | 3 (uniform) | mildly unbounded |

**Cell Péclet number** sets where central differencing fails:

\[
\mathrm{Pe}_{\text{cell}} = \frac{\rho u \Delta x}{\Gamma}, \qquad \text{oscillations for } \mathrm{Pe}_{\text{cell}} > 2
\]

**TVD condition.** A limiter \(\psi(r)\) is second-order TVD if it lies in the Sweby region:

\[
\psi(r) = 0 \;\;(r \le 0), \qquad \psi(r) \le \min(2r,\,2), \qquad \psi(1)=1
\]

minmod \(=\max(0,\min(1,r))\) is the most diffusive; van Leer \(=(r+|r|)/(1+|r|)\) is a good default; superbee sits on the upper bound and artificially steepens smooth gradients.

**Gradient reconstruction:**

\[
\text{Green–Gauss:}\quad \nabla\phi_P = \frac{1}{V_P}\sum_f \phi_f \mathbf{n}_f A_f
\qquad
\text{Least squares:}\quad \min_{\nabla\phi}\sum_N w_N\left(\phi_N - \phi_P - \nabla\phi\cdot\mathbf{d}_{PN}\right)^2
\]

**Non-orthogonal correction.** The diffusive flux needs \(\partial\phi/\partial n\) at the face. When \(\mathbf{d}_{PN}\) is not parallel to \(\mathbf{n}_f\), split into an implicit orthogonal part and an explicit correction:

\[
\nabla\phi\cdot\mathbf{n}_f A_f
= \underbrace{|\boldsymbol{\Delta}|\frac{\phi_N - \phi_P}{|\mathbf{d}_{PN}|}}_{\text{implicit}}
+ \underbrace{\overline{\nabla\phi}_f\cdot\mathbf{k}}_{\text{explicit correction}}
\]

## Mental model

Every FV scheme is a bookkeeping system over boxes. The only physics enters at the faces, and the only art is deciding what value to use there given cell averages on both sides.

Upwinding is a statement about causality: take the value from the side the flow came from. First-order upwind is exactly a one-cell-wide numerical diffusion with coefficient \(\Gamma_{\text{num}} = \rho u \Delta x/2\) — which is why coarse first-order runs look laminar and smooth regardless of \(\mathrm{Re}\).

## Numerics / practice

- **Least-squares gradients** on anything unstructured or irregular. Green–Gauss only where the mesh is near-uniform and near-orthogonal.
- **Deferred correction** is the standard way to run a high-order scheme with a low-order implicit matrix: implicit upwind, explicit \((\text{HO} - \text{UD})\) on the right-hand side. Stable, but the explicit part limits convergence rate.
- **Report mesh quality** — maximum non-orthogonality, skewness, aspect ratio — with every result. These numbers explain more failures than the scheme choice does.
- **Verify with MMS.** Manufactured solutions are the only way to confirm the implemented order of accuracy on a real mesh.

??? warning "Failure modes"
    **Central differencing above \(\mathrm{Pe}_{\text{cell}}=2\).** Node-to-node oscillations in convection-dominated regions. The classic wrong fix is refining until \(\mathrm{Pe}_{\text{cell}} < 2\) everywhere, which at high \(\mathrm{Re}\) is unaffordable. The right fix is a bounded scheme.

    **First-order upwind used "to get it converging".** It always converges, because it adds diffusion proportional to \(\Delta x\). At typical mesh sizes the numerical diffusion exceeds the physical viscosity by orders of magnitude — the result is a converged solution to a different problem. If a case only runs first order, that is a diagnosis, not a solution.

    **Green–Gauss on skewed or irregular meshes.** Degrades to inconsistent — the error does not vanish under refinement if mesh irregularity is preserved. Symptom: gradients that look plausible but produce wrong diffusive fluxes, worst in boundary layers with high aspect ratio.

    **Unbounded higher-order schemes on scalars with physical bounds.** Volume fractions outside \([0,1]\), negative species mass fractions, negative \(k\). These often crash the run several steps later in an unrelated place, so the traceback misleads.

    **Explicit non-orthogonal correction ignored or under-iterated.** On meshes beyond ~70° non-orthogonality, one correction pass is not enough; the diffusive flux is simply wrong. Symptom: results that change with the number of non-orthogonal corrector loops — if they do, you have not converged in that loop.

    **Limiters destroying convergence to steady state.** The limiter switches between iterations and the residual stalls. Freeze it after the residual has dropped a few decades, or use a differentiable one.

    **Assuming FV conservation implies accuracy.** Conservation is exact regardless of how bad the face values are. A wildly inaccurate solution can conserve mass perfectly. Global balance checks are necessary, never sufficient.

    <!-- Add your own here. -->

## Worked example

The numerical diffusion of first-order upwind, against the physical value:

```python
rho, u, dx, mu = 1.2, 20.0, 0.01, 1.8e-5
gamma_num = rho * u * dx / 2.0
print(f"numerical diffusivity : {gamma_num:.4f} kg/m/s")
print(f"physical viscosity    : {mu:.2e} kg/m/s")
print(f"ratio                 : {gamma_num/mu:,.0f}x")
print(f"effective Re          : {rho*u*1.0/gamma_num:.1f} (intended {rho*u*1.0/mu:.0f})")
```

```
numerical diffusivity : 0.1200 kg/m/s
physical viscosity    : 1.80e-05 kg/m/s
ratio                 : 6,667x
effective Re          : 200.0 (intended 1333333)
```

A 10 mm cell at 20 m/s turns an intended \(\mathrm{Re}=1.3\times10^6\) into an effective \(\mathrm{Re}=200\). The run will be stable, smooth, converged, and meaningless.

## Connections

- **[Sod shock tube notebook](../../notebooks/sod-shock-tube.ipynb)** — reconstruction order and numerical diffusion, measured.
- [Governing equations](../governing-equations.md) — the integral form FV discretizes.
- [Compressible flow](../compressible.md) — Riemann solvers as the face-flux answer.
- [Time integration](time-integration.md) — what to do with the resulting ODE system.
- [Meshing](meshing.md) — the quality metrics referenced above.

## Sources

- Ferziger, Perić & Street, *Computational Methods for Fluid Dynamics*.
- Moukalled, Mangani & Darwish, *The Finite Volume Method in Computational Fluid Dynamics* — unstructured details, non-orthogonal corrections.
- Archive: `Others/Jameson`; see the [course archive](../../resources/course-archive.md).
