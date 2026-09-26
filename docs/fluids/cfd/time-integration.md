---
title: Time integration
status: solid
tags: [pillar-4, fluids, cfd, cfl, stability]
updated: 2026-09-26
---

# Time integration

<span class="status status-solid">solid</span>
<span class="pillar">pillar 4 &middot; Solvers, time integration and adjoints</span>

!!! abstract "In one minute"
    - Discretizing space turns the PDE into \(d\mathbf{U}/dt = \mathbf{R}(\mathbf{U})\). Stability is then the question of whether \(\Delta t\lambda\) lies inside the scheme's stability region for every eigenvalue \(\lambda\).
    - **Convection limits \(\Delta t \sim \Delta x\); diffusion limits \(\Delta t \sim \Delta x^2\).** The second is the one people forget, and it dominates on fine meshes.
    - Implicit removes the stability limit, never the **accuracy** limit. A large \(\Delta t\) that is stable can still be wrong.
    - For steady state, **local time stepping** and multigrid are pseudo-time accelerators — and they destroy time accuracy by design.
    - **Stability and accuracy are separate questions.** A scheme can be unconditionally stable and badly inaccurate; CFL < 1 guarantees neither convergence nor correctness.

## Key results

**Semi-discrete form and the CFL condition:**

<div class="result" markdown>

\[
\frac{d\mathbf{U}}{dt} = \mathbf{R}(\mathbf{U}),
\qquad
\mathrm{CFL} = \frac{|u| \Delta t}{\Delta x} \le C_{\max},
\qquad
\Delta t_{\text{diff}} \le \frac{\Delta x^2}{2\nu\,d}
\]

for \(d\) spatial dimensions. Combined, \(\Delta t \le \left(\frac{|u|}{\Delta x} + \frac{2\nu d}{\Delta x^2}\right)^{-1}\).

</div>

**Explicit schemes:**

| Scheme | Order | \(C_{\max}\) (1D advection) | Notes |
|---|---|---|---|
| Forward Euler | 1 | unstable with central space | needs upwinding |
| RK2 (Heun) | 2 | ~1.0 | cheap, common in FV |
| RK3-SSP | 3 | 1.0 | preserves TVD of the spatial operator |
| RK4 | 4 | ~2.8 | large stability region, 4 residual evaluations |

**Implicit schemes:**

\[
\text{Backward Euler:}\quad \frac{\mathbf{U}^{n+1}-\mathbf{U}^n}{\Delta t} = \mathbf{R}(\mathbf{U}^{n+1})
\qquad
\text{BDF2:}\quad \frac{3\mathbf{U}^{n+1}-4\mathbf{U}^n+\mathbf{U}^{n-1}}{2\Delta t} = \mathbf{R}(\mathbf{U}^{n+1})
\]

Backward Euler is L-stable and first order — very damping, which is why it is excellent for steady state and poor for unsteady. BDF2 is second order and A-stable, the usual production default. Crank–Nicolson is second order and A-stable but **not** L-stable: it fails to damp high-frequency modes and rings.

**Dual time stepping** for unsteady compressible work: wrap a physical-time BDF term inside a pseudo-time march, so steady-state accelerators (local \(\Delta t\), multigrid) can be used inside each physical step:

\[
\frac{\partial \mathbf{U}}{\partial \tau} + \underbrace{\frac{3\mathbf{U}-4\mathbf{U}^n+\mathbf{U}^{n-1}}{2\Delta t} - \mathbf{R}(\mathbf{U})}_{\text{drive to zero in }\tau} = 0
\]

**Stiffness.** When \(\lambda_{\max}/\lambda_{\min}\) is large — acoustic vs convective speeds at low Mach, or fast chemistry against flow time — explicit stepping is bound by the fastest mode even when it carries no energy. Options: implicit, IMEX (implicit on the stiff term only), or operator splitting.

## Mental model

Plot the eigenvalues of \(\partial\mathbf{R}/\partial\mathbf{U}\), scaled by \(\Delta t\), on the complex plane. Explicit schemes have a bounded stability region near the origin; every scaled eigenvalue must lie inside it. Pure advection puts eigenvalues on the imaginary axis (so a scheme needs imaginary-axis coverage — forward Euler has none, hence its failure with central differencing). Pure diffusion puts them on the negative real axis. Implicit schemes cover the whole left half-plane, which is what "unconditionally stable" means — and says nothing about accuracy.

## Numerics / practice

- **Compute both limits** and use the minimum. On fine boundary-layer meshes the diffusive limit usually wins by a wide margin.
- **Choose \(\Delta t\) from physics for unsteady runs**: resolve the shedding period or acoustic timescale with 20–100 steps, then check CFL is satisfied rather than the reverse.
- **Report inner-iteration convergence.** An implicit step whose Newton/Krylov loop is loosely converged is an explicit step wearing a disguise, and the time accuracy claim is void.
- **Verify order in time** by refining \(\Delta t\) on a fixed mesh. Spatial and temporal convergence studies must be done separately, or they contaminate each other.

??? warning "Failure modes"
    **Forgetting the diffusive limit.** Halving \(\Delta x\) halves the convective \(\Delta t\) but quarters the diffusive one. On a fine viscous mesh the run becomes unaffordable for reasons that look inexplicable if only CFL is being monitored. Symptom: an explicit run that was fine at one mesh level dies on the next.

    **CFL satisfied, still unstable.** The linear CFL condition is derived for a linear, constant-coefficient problem. Nonlinearities, source terms, boundary treatments and variable coefficients all tighten it. A CFL of 0.9 is not a guarantee; if it diverges, reduce it and look for the real cause.

    **Crank–Nicolson ringing.** A-stable but not L-stable, so high-frequency modes are not damped, only rotated. Symptom: persistent oscillation at the grid scale after a sharp transient or an impulsive start, that refinement in space does not remove. Fix: BDF2, or blend towards backward Euler.

    **Local time stepping in an unsteady run.** Each cell advances at its own \(\Delta t\), so the solution is not synchronous and means nothing in physical time. Easy to leave on accidentally when converting a steady case to unsteady — and the run looks perfectly healthy.

    **Loose inner tolerance on an implicit step.** With a nominally second-order BDF2 outer scheme, an under-converged inner solve degrades it to first order or worse. Symptom: time-refinement study shows an order far below the scheme's nominal one.

    **Startup transients treated as physics.** An impulsive start injects a broadband acoustic pulse. Statistics gathered before it leaves the domain are contaminated. Discard the first few flow-through times, and state how many.

    **Stiff source terms integrated explicitly.** Chemistry or turbulence source terms can have timescales orders of magnitude below the flow's. Symptom: negative species or negative \(k\) appearing in a single step. Fix: implicit treatment or splitting for the source alone.

    <!-- Add your own here. -->

## Worked example

Which limit actually binds, across a mesh refinement:

```python
u, nu, d = 20.0, 1.5e-5, 3
for dx in (1e-2, 1e-3, 1e-4):
    dt_c = dx / u
    dt_d = dx**2 / (2 * nu * d)
    print(f"dx={dx:.0e}  dt_conv={dt_c:.2e}  dt_diff={dt_d:.2e}  "
          f"binding: {'diffusion' if dt_d < dt_c else 'convection'}")
```

```
dx=1e-02  dt_conv=5.00e-04  dt_diff=1.11e+00  binding: convection
dx=1e-03  dt_conv=5.00e-05  dt_diff=1.11e-02  binding: convection
dx=1e-04  dt_conv=5.00e-06  dt_diff=1.11e-04  binding: convection
```

Convection binds throughout this range, but the diffusive limit closes by a factor of 10 per refinement level. The crossover is at \(\Delta x^{*} = 2\nu d/|u| = 4.5\,\mu\mathrm{m}\) here — inside a boundary-layer mesh, not outside it. Compute both; do not assume.

## Connections

- [Finite volume](finite-volume.md) — where \(\mathbf{R}(\mathbf{U})\) comes from.
- [Compressible flow](../compressible.md) — hyperbolic wave speeds in the CFL number.
- [Incompressible flow](../incompressible.md) — projection schemes and their time accuracy.
- [Foundations › Linear solvers](../../foundations/index.md) — the implicit solve itself.

## Sources

- Hirsch, *Numerical Computation of Internal and External Flows* — stability analysis in depth.
- LeVeque, *Finite Volume Methods for Hyperbolic Problems* — CFL and SSP schemes.
- Archive: see the [course archive](../../resources/course-archive.md).
