---
title: Governing equations
status: solid
tags: [pillar-1, fluids, conservation-laws, scaling]
updated: 2026-09-26
---

# Governing equations

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Continuity, momentum and energy are one statement repeated: **flux in minus flux out equals rate of change**, applied to mass, momentum and total energy.
    - Navier–Stokes is that statement plus a **constitutive closure** — Newtonian stress linear in strain rate — not a fundamental law.
    - **Conservative (divergence) form is not cosmetic.** Discretize the non-conservative form and shocks move at the wrong speed.
    - Nondimensionalization tells you which terms you may drop. \(\mathrm{Re}\), \(\mathrm{Ma}\), \(\mathrm{Pr}\), \(\mathrm{Fr}\) are the regime coordinates.
    - Everything downstream — schemes, closures, boundary conditions — is decided by the **character** of the resulting PDE system, not by its physical name.

## Key results

**Conservative form.** For a conserved density \(\phi\) with flux \(\mathbf{F}\) and source \(S\):

\[
\frac{\partial \phi}{\partial t} + \nabla\cdot\mathbf{F}(\phi) = S
\]

Every equation below is an instance of this.

<div class="result" markdown>

**Mass**

\[
\frac{\partial \rho}{\partial t} + \nabla\cdot(\rho\mathbf{u}) = 0
\]

**Momentum**

\[
\frac{\partial (\rho\mathbf{u})}{\partial t} + \nabla\cdot(\rho\mathbf{u}\otimes\mathbf{u})
= -\nabla p + \nabla\cdot\boldsymbol{\tau} + \rho\mathbf{g}
\]

**Total energy** \(E = \rho e + \tfrac{1}{2}\rho|\mathbf{u}|^2\)

\[
\frac{\partial E}{\partial t} + \nabla\cdot\big[(E + p)\mathbf{u}\big]
= \nabla\cdot(\boldsymbol{\tau}\cdot\mathbf{u}) - \nabla\cdot\mathbf{q} + \rho\mathbf{g}\cdot\mathbf{u}
\]

</div>

**Newtonian closure**, with \(\lambda = -\tfrac{2}{3}\mu\) under Stokes' hypothesis:

\[
\boldsymbol{\tau} = \mu\left(\nabla\mathbf{u} + \nabla\mathbf{u}^{\mathsf T}\right)
+ \lambda(\nabla\cdot\mathbf{u})\mathbf{I},
\qquad
\mathbf{q} = -k\nabla T
\]

Closed by an equation of state, \(p = \rho R T\) for a calorically perfect gas.

**Nondimensional groups.** With reference \(U, L, \rho_\infty\):

| Group | Definition | Compares | Small means |
|---|---|---|---|
| \(\mathrm{Re}\) | \(\rho U L/\mu\) | inertia : viscous | viscous-dominated, Stokes flow |
| \(\mathrm{Ma}\) | \(U/a\) | speed : sound speed | effectively incompressible |
| \(\mathrm{Pr}\) | \(\nu/\alpha\) | momentum : thermal diffusion | thermal layer thicker than velocity layer |
| \(\mathrm{Fr}\) | \(U/\sqrt{gL}\) | inertia : gravity | stratification/gravity dominant |
| \(\mathrm{Pe}\) | \(\mathrm{Re}\,\mathrm{Pr}\) | advection : diffusion | diffusion-dominated |

**Incompressible limit.** \(\mathrm{Ma}\to 0\) gives \(\nabla\cdot\mathbf{u}=0\), and pressure stops being a thermodynamic variable — it becomes the Lagrange multiplier enforcing that constraint. This changes the *type* of the system, not just its coefficients.

## Mental model

Write a box in the flow. Whatever is inside changes only because something crossed the boundary or was created inside. That is the whole content of the divergence form, and it is why finite volume is the natural discretization: it enforces the box statement exactly, at machine precision, for every cell.

The character of the system follows from what carries information:

- **Hyperbolic** (Euler, high \(\mathrm{Re}\)): finite-speed characteristics, domains of dependence, discontinuities permitted.
- **Parabolic** (boundary layer, unsteady diffusion): infinite signal speed, smoothing, marching in time.
- **Elliptic** (incompressible pressure, potential flow): instantaneous global coupling, boundary data felt everywhere at once.

Most real systems are mixed, and the mixture dictates the algorithm.

## Numerics / practice

**Work in conservative variables** \((\rho, \rho\mathbf{u}, E)\) for compressible flow. The Lax–Wendroff theorem guarantees that *if* a consistent conservative scheme converges, it converges to a weak solution with correct jump conditions. No such guarantee exists otherwise.

**Nondimensionalize before coding.** It sets sane magnitudes for residuals and tolerances, exposes stiffness, and makes verification portable across scales.

**Check which terms survive.** At \(\mathrm{Re}=10^7\) viscous terms matter only in thin layers; at \(\mathrm{Ma}=0.05\) acoustic terms are stiff noise. The equations you solve should reflect the regime you are in.

??? warning "Failure modes"
    **Non-conservative form on discontinuities.** Solving \(\partial_t u + u\,\partial_x u = 0\) instead of \(\partial_t u + \partial_x(u^2/2) = 0\) produces a shock that travels at the wrong speed. The run converges cleanly and the answer is wrong — no oscillation, no warning. The most dangerous failure on this page.

    **Stokes' hypothesis assumed silently.** \(\lambda = -\tfrac{2}{3}\mu\) is an assumption, not a law. It fails for bulk-viscosity-sensitive problems: acoustic attenuation, shock structure in polyatomic gases, hypersonic relaxation.

    **Low-Mach stiffness.** As \(\mathrm{Ma}\to 0\) the acoustic eigenvalues \(u \pm a\) vastly exceed \(u\). An explicit compressible code is then limited by a wave speed carrying almost no energy — timestep collapses while nothing physical happens fast. Symptom: absurdly small \(\Delta t\), and pressure checkerboarding as the pressure–velocity coupling degenerates. Fix with preconditioning or switch to an incompressible formulation.

    **Boussinesq buoyancy outside its range.** Valid only for small density variation, typically \(\Delta\rho/\rho \lesssim 0.1\). Applied to fire plumes or strongly heated flows it silently loses the dominant buoyancy term.

    **Inconsistent reference state.** Mixing dimensional and nondimensional quantities — a dimensional viscosity with nondimensional velocities — yields an effective Reynolds number nothing like the intended one. Symptom: results that look physical but sit in the wrong regime. Always print the realised \(\mathrm{Re}\) and \(\mathrm{Ma}\) at startup.

    <!-- Add your own here: the ones that actually cost you time. -->

## Worked example

Confirm which terms you are entitled to drop before writing a solver:

```python
import numpy as np

U, L, rho, mu, gamma, R, T = 30.0, 2.0, 1.2, 1.8e-5, 1.4, 287.0, 293.0
a  = np.sqrt(gamma * R * T)
Re = rho * U * L / mu
Ma = U / a

print(f"Re = {Re:.3e}   Ma = {Ma:.3f}   a = {a:.1f} m/s")
print("incompressible (Ma^2 << 1):", Ma**2 < 0.01)
print("viscous layer thickness ~ L/sqrt(Re) =", L / np.sqrt(Re), "m")
```

`Re = 4.000e+06  Ma = 0.087` — incompressible is justified (\(\mathrm{Ma}^2 = 0.0076\)), and viscous effects are confined to a layer around 1 mm.

## Connections

- [Incompressible flow](incompressible.md) — what the \(\mathrm{Ma}\to 0\) limit does to the algorithm.
- Compressible flow — the hyperbolic branch, and shocks. *(pending; see [Fluids](index.md))*
- Finite volume — why the box statement discretizes so naturally. *(pending)*
- Turbulence — what averaging these equations costs. *(pending)*

## Sources

- Archive: `Others/Jameson` — CFD and aerodynamic shape optimization.
- Archive: see the [course archive](../resources/course-archive.md) for the Mechanical and Aerospace fluid-mechanics folders.
- Batchelor, *An Introduction to Fluid Dynamics* — conservation laws and constitutive relations.
- Leveque, *Finite Volume Methods for Hyperbolic Problems* — conservative form and weak solutions.
