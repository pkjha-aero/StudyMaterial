---
title: Incompressible flow
status: solid
tags: [pillar-1, pillar-4, fluids, pressure-velocity-coupling, projection]
updated: 2026-09-26
---

# Incompressible flow

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - There is no evolution equation for pressure. \(p\) is the **Lagrange multiplier** enforcing \(\nabla\cdot\mathbf{u}=0\), and it adjusts instantaneously and globally.
    - Every incompressible algorithm is a way of answering: *what pressure field makes the velocity divergence-free?* That is a Poisson solve, and it dominates the cost.
    - **Projection** (Chorin) and **pressure-correction** (SIMPLE/PISO) are the same idea at different points in the accuracy/robustness trade.
    - Collocated grids need **Rhie–Chow** interpolation, or the pressure decouples into a checkerboard the solver cannot see.
    - The elliptic pressure equation makes the problem globally coupled: parallel scaling is dictated by the Poisson solver, not the flow.

## Key results

<div class="result" markdown>

\[
\nabla\cdot\mathbf{u} = 0,
\qquad
\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u}
= -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u} + \mathbf{f}
\]

</div>

**Pressure Poisson equation.** Take the divergence of momentum and impose \(\nabla\cdot\mathbf{u}=0\):

\[
\nabla^2 p = -\rho\,\nabla\cdot\big[(\mathbf{u}\cdot\nabla)\mathbf{u}\big]
= -\rho\,\frac{\partial u_i}{\partial x_j}\frac{\partial u_j}{\partial x_i}
\]

**Fractional step / projection.** Advance to an intermediate velocity ignoring pressure, then project onto the divergence-free space:

\[
\frac{\mathbf{u}^* - \mathbf{u}^n}{\Delta t} = -(\mathbf{u}\cdot\nabla)\mathbf{u} + \nu\nabla^2\mathbf{u},
\qquad
\nabla^2 p^{n+1} = \frac{\rho}{\Delta t}\nabla\cdot\mathbf{u}^*,
\qquad
\mathbf{u}^{n+1} = \mathbf{u}^* - \frac{\Delta t}{\rho}\nabla p^{n+1}
\]

This is a Helmholtz–Hodge decomposition: any vector field splits uniquely into a divergence-free part and a gradient.

**SIMPLE**, for steady problems — solve momentum with a guessed \(p^*\), derive a correction \(p'\) from the continuity defect, under-relax, repeat:

\[
p = p^* + \alpha_p\, p',
\qquad
\alpha_p \approx 0.3,\; \alpha_u \approx 0.7 \quad (\alpha_p + \alpha_u \approx 1)
\]

**PISO** adds corrector steps per timestep instead of outer iterations — better for transient work.

**Rhie–Chow.** On a collocated grid, interpolate face velocities with a pressure-gradient correction rather than averaging:

\[
u_f = \overline{u}_f - \overline{d}_f\left(\frac{\partial p}{\partial x}\bigg|_f - \overline{\frac{\partial p}{\partial x}}\bigg|_f\right)
\]

The correction term is what couples adjacent pressure nodes.

## Mental model

Compressible flow lets pressure disturbances travel at finite speed \(a\). Incompressible flow is the \(a\to\infty\) limit: squeeze the fluid anywhere and every other point knows immediately. That is why pressure is elliptic and why there is no such thing as a local incompressible solve.

Projection has a clean geometric reading. \(\mathbf{u}^*\) has drifted off the divergence-free subspace; the pressure gradient is exactly the component that must be subtracted to put it back. Nothing about pressure here is thermodynamic.

## Numerics / practice

- **Staggered grids** (velocities on faces, pressure at centres) couple pressure and velocity naturally and need no Rhie–Chow. They are awkward on unstructured meshes, which is why collocated + Rhie–Chow dominates general-purpose codes.
- **Poisson solve is the cost centre.** Use multigrid or a Krylov method with a multigrid preconditioner; direct solvers do not scale. Expect 60–80% of runtime here.
- **Pressure boundary conditions** are a consequence, not a choice: with Dirichlet velocity everywhere, pressure gets homogeneous Neumann conditions, the system is singular up to a constant, and you must pin a reference value or project the constant out.
- **Time accuracy.** Standard projection is formally first-order in pressure unless you use an incremental/rotational form.

??? warning "Failure modes"
    **Checkerboard pressure.** On a collocated grid with plain central interpolation, a pressure field alternating \(+1,-1,+1,\dots\) has zero discrete gradient at every node: the momentum equation cannot see it. Symptom: oscillatory pressure on the cell scale with a perfectly smooth velocity field. Cause: no odd–even coupling. Fix: Rhie–Chow, or stagger.

    **Singular Poisson system left unpinned.** All-Neumann pressure BCs leave the constant undetermined. Krylov solvers stall or wander, and the reported residual may still look acceptable. Fix: fix one reference cell, or project the null space out each iteration — and make sure the right-hand side is compatible (integrates to zero), which it will not be if your boundary mass flux is unbalanced.

    **Mass imbalance at boundaries.** If inflow and outflow fluxes do not sum to zero to machine precision, the Poisson problem is inconsistent and cannot converge. Symptom: pressure residual plateaus at a fixed value no matter the solver. Always rescale the outflow.

    **Over-tight under-relaxation in SIMPLE.** Too small and convergence crawls; too large and it diverges. \(\alpha_p + \alpha_u \approx 1\) is the useful heuristic. A run that stalls at a residual of \(10^{-3}\) is usually under-relaxation, not mesh.

    **Projection at high aspect ratio.** Stretched boundary-layer cells make the Poisson operator badly conditioned. Multigrid convergence degrades sharply — the fix is semi-coarsening or line relaxation in the stretched direction, not more iterations.

    **Treating the intermediate velocity as physical.** \(\mathbf{u}^*\) does not satisfy the boundary conditions or continuity. Sampling it for output, or for coupling to another solver, silently introduces error.

    <!-- Add your own here. -->

## Worked example

Checkerboarding is easiest to believe when you watch a central difference annihilate it:

```python
import numpy as np

n = 8
p_checker = np.array([(-1.0)**i for i in range(n)])      # +1,-1,+1,...
grad = (p_checker[2:] - p_checker[:-2]) / 2.0            # central difference

print("pressure :", p_checker)
print("gradient :", grad)                                 # all zeros
print("momentum equation sees this field as:", np.abs(grad).max())
```

The gradient is identically zero, so the momentum equation is blind to a pressure oscillation of amplitude 1. Nothing in the residual will report it.

## Connections

- [Governing equations](governing-equations.md) — where the constraint comes from.
- [Finite volume](cfd/finite-volume.md) — flux assembly and face interpolation.
- [Time integration](cfd/time-integration.md) — projection versus fully coupled schemes.
- [Foundations › Linear solvers](../foundations/index.md) — multigrid for the Poisson stage.

## Sources

- Ferziger, Perić & Street, *Computational Methods for Fluid Dynamics* — SIMPLE, PISO, Rhie–Chow.
- Chorin (1968), *Numerical solution of the Navier–Stokes equations* — the original projection method.
- Archive: see the [course archive](../resources/course-archive.md).
