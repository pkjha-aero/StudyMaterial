---
title: Compressible flow
status: solid
tags: [pillar-1, pillar-3, fluids, shocks, riemann, godunov]
updated: 2026-09-26
---

# Compressible flow

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - The Euler equations are **hyperbolic**: information travels along characteristics at \(u-a\), \(u\), \(u+a\). Everything numerical follows from that.
    - Solutions develop **discontinuities from smooth data**. Weak solutions, not classical ones, are what you are computing.
    - The **Riemann problem** — a single jump between two constant states — is the local building block. Godunov schemes solve one per face per step.
    - Second order plus discontinuities means oscillations unless you **limit**. Godunov's theorem says linear monotone schemes are at best first order.
    - **Conservative form is mandatory.** Get it wrong and shocks travel at the wrong speed, quietly.

## Key results

**Euler equations** in 1D conservative form, \(\mathbf{U} = (\rho, \rho u, E)^{\mathsf T}\):

<div class="result" markdown>

\[
\frac{\partial \mathbf{U}}{\partial t} + \frac{\partial \mathbf{F}(\mathbf{U})}{\partial x} = 0,
\qquad
\mathbf{F} = \begin{pmatrix} \rho u \\ \rho u^2 + p \\ (E+p)u \end{pmatrix}
\]

Flux Jacobian eigenvalues: \(\lambda = u - a,\; u,\; u + a\), with \(a = \sqrt{\gamma p/\rho}\).

</div>

**Rankine–Hugoniot.** A discontinuity moving at speed \(s\) satisfies

\[
s\,[\![\mathbf{U}]\!] = [\![\mathbf{F}(\mathbf{U})]\!]
\]

This is the relation that a non-conservative discretization violates.

**Normal shock**, upstream Mach \(M_1\):

\[
\frac{\rho_2}{\rho_1} = \frac{(\gamma+1)M_1^2}{(\gamma-1)M_1^2 + 2},
\qquad
\frac{p_2}{p_1} = \frac{2\gamma M_1^2 - (\gamma-1)}{\gamma+1},
\qquad
M_2^2 = \frac{(\gamma-1)M_1^2 + 2}{2\gamma M_1^2 - (\gamma-1)}
\]

Entropy requires \(M_1 \ge 1\): compression shocks only. Expansion shocks are mathematically admissible weak solutions and physically forbidden — a distinction your scheme must enforce.

**Godunov update.** Exact for the piecewise-constant Riemann problem at each face:

\[
\mathbf{U}_i^{n+1} = \mathbf{U}_i^n - \frac{\Delta t}{\Delta x}\left(\mathbf{F}_{i+1/2} - \mathbf{F}_{i-1/2}\right)
\]

**Approximate Riemann solvers**, in increasing order of cost and fidelity:

| Solver | Waves resolved | Notes |
|---|---|---|
| Rusanov / Lax–Friedrichs | none | maximum wave speed only; very dissipative, very robust |
| HLL | 2 (fastest left/right) | contact smeared badly |
| HLLC | 3 (adds contact) | good default for most work |
| Roe | all, linearized | sharpest; needs an entropy fix, can fail on strong rarefactions |

**MUSCL reconstruction** with a slope limiter \(\psi(r)\) gives second order away from extrema while staying TVD:

\[
\mathbf{U}_{i+1/2}^{L} = \mathbf{U}_i + \tfrac{1}{2}\psi(r_i)\,(\mathbf{U}_i - \mathbf{U}_{i-1}),
\qquad
r_i = \frac{\mathbf{U}_{i+1} - \mathbf{U}_i}{\mathbf{U}_i - \mathbf{U}_{i-1}}
\]

minmod is the most dissipative and most robust; van Leer and superbee are progressively sharper, superbee to the point of artificially steepening smooth profiles.

## Mental model

Think in characteristics. At any point three signals pass: two acoustic, one entropy/contact travelling with the fluid. Supersonic flow means all three point downstream — nothing propagates upstream, which is why supersonic outflow needs no boundary condition and subsonic outflow needs exactly one.

A shock is where characteristics converge and cross. Since a single-valued solution cannot have crossing characteristics, the solution must jump — the discontinuity is not a modelling artefact but the only consistent outcome.

## Numerics / practice

- **Reconstruct in primitive or characteristic variables**, not conservative ones. Limiting conservative variables couples the fields and produces spurious pressure oscillations at contacts.
- **Entropy fix for Roe.** The linearization admits expansion shocks at sonic points. Harten's fix smooths the eigenvalue near zero.
- **Positivity.** Strong shocks or near-vacuum states can drive the reconstructed density or pressure negative. HLLC with a positivity-preserving limiter is the practical answer.
- **Non-reflecting boundaries.** Characteristic-based (NSCBC) conditions, or a sponge layer. A plain extrapolation outflow reflects acoustic waves back into the domain.

??? warning "Failure modes"
    **Carbuncle phenomenon.** Low-dissipation solvers (Roe, HLLC) on a grid-aligned strong bow shock develop a protrusion along the stagnation line. Symptom: a bulge or spike in the shock exactly on the symmetry axis, worsening with refinement. Cause: insufficient cross-flow dissipation on aligned grids. Fixes: hybrid flux (switch to HLL near shocks), rotated Riemann solvers, or deliberately non-aligned grids. It is a scheme pathology, not a mesh error, and refining makes it worse — the opposite of the usual diagnosis.

    **Entropy-violating expansion shock.** Roe without an entropy fix produces a stationary discontinuity in an expansion fan at a sonic point. Symptom: a sharp jump where a smooth fan belongs. Silent — the solution is a valid weak solution, just the wrong one.

    **Limiter cycling.** Steady-state residuals stall at \(10^{-4}\)–\(10^{-6}\) and oscillate. Cause: the limiter switches state between iterations, so the operator is not differentiable. Fix: a differentiable limiter (van Albada), or freeze the limiter once the residual has dropped.

    **Low-Mach accuracy loss.** Standard upwind fluxes have dissipation scaling as \(1/\mathrm{Ma}\) in the pressure term, so at \(\mathrm{Ma} \lesssim 0.1\) the solution degrades towards nonsense even though it converges. Not the same problem as low-Mach *stiffness* — this is an accuracy failure, not a timestep one. Fix: low-Mach preconditioning or a flux with correct asymptotic scaling.

    **Limiting conservative variables.** Produces pressure oscillations at contact discontinuities where density jumps but pressure should not. Symptom: pressure wiggles that refine away slowly, tracking material interfaces.

    **Reflecting outflow.** Zeroth-order extrapolation at a subsonic outlet reflects acoustic energy. Symptom: a slow drift or standing oscillation in the whole domain that never settles.

    <!-- Add your own here. -->

## Worked example

The eigenvalues tell you what your boundary conditions must supply:

```python
import numpy as np

gamma = 1.4
for rho, u, p in [(1.0, 100.0, 1e5), (1.0, 500.0, 1e5)]:
    a = np.sqrt(gamma * p / rho)
    lam = np.array([u - a, u, u + a])
    n_in = int((lam < 0).sum())          # characteristics entering at a right boundary
    print(f"M={u/a:.2f}  eigenvalues={np.round(lam,1)}  "
          f"BCs needed at outflow: {n_in}")
```

```
M=0.27  eigenvalues=[-274.2  100.   474.2]  BCs needed at outflow: 1
M=1.34  eigenvalues=[ 125.8  500.   874.2]  BCs needed at outflow: 0
```

Subsonic outflow needs exactly one condition — normally back pressure. Supersonic outflow needs none, and imposing one over-determines the problem.

## Connections

- [Governing equations](governing-equations.md) — why conservative form is not optional.
- [Finite volume](cfd/finite-volume.md) — the flux machinery these solvers plug into.
- [Time integration](cfd/time-integration.md) — CFL for hyperbolic systems.
- [Incompressible flow](incompressible.md) — the other limit, and why it needs a different algorithm.

## Sources

- Toro, *Riemann Solvers and Numerical Methods for Fluid Dynamics* — the standard reference for everything above.
- LeVeque, *Finite Volume Methods for Hyperbolic Problems* — weak solutions, limiters, TVD theory.
- Archive: `Others/Jameson` — CFD and aerodynamic shape optimization.
- Archive: see the [course archive](../resources/course-archive.md).
