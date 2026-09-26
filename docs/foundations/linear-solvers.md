---
title: Linear solvers
status: solid
tags: [pillar-4, foundations, scaling]
updated: 2026-09-26
---

# Linear solvers

<span class="status status-solid">solid</span>
<span class="pillar">pillar 4 &middot; Solvers, time integration and adjoints</span>

!!! abstract "In one minute"
    - Direct solvers are robust and scale badly: \(O(N^3)\) dense, and sparse LU suffers **fill-in** that destroys sparsity.
    - Krylov methods cost matrix–vector products and converge at a rate set by the **spectrum**, not the matrix size.
    - **Preconditioning is the whole game.** An unpreconditioned Krylov solver on a real PDE system is not competitive.
    - **Multigrid is \(O(N)\)** when it works, because it attacks each error wavelength on the grid where that wavelength is cheap to smooth.
    - A small **residual is not a small error** — the gap is the condition number, and this misreading is everywhere.

## Key results

**Cost comparison** for a sparse system from a 3D PDE with \(N\) unknowns:

<div class="result" markdown>

| Method | Work | Memory | Notes |
|---|---|---|---|
| Dense LU | \(O(N^3)\) | \(O(N^2)\) | only for small dense blocks |
| Sparse LU | \(\sim O(N^2)\) | fill-in dependent | robust; memory is the wall |
| CG (SPD) | \(O(N\sqrt{\kappa})\) | \(O(N)\) | short recurrence, cheap |
| GMRES | \(O(N)\) per iter, growing | \(O(Nm)\) for \(m\) vectors | general matrices; restart needed |
| Multigrid | \(O(N)\) | \(O(N)\) | needs a good smoother/coarsening |

</div>

**Krylov convergence.** CG on an SPD system satisfies

\[
\frac{\|\mathbf{e}_k\|_A}{\|\mathbf{e}_0\|_A} \le 2\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^{k}
\]

so iterations scale as \(\sqrt{\kappa}\). For a Poisson problem \(\kappa \sim h^{-2}\), giving \(O(h^{-1})\) iterations — halving \(h\) doubles the iteration count, before preconditioning.

More sharply: convergence depends on the **clustering** of eigenvalues, not just their extremes. A preconditioner that clusters the spectrum wins even without reducing \(\kappa\) much.

**Method selection:**

| Matrix | Method |
|---|---|
| Symmetric positive definite | CG |
| Symmetric indefinite | MINRES |
| Nonsymmetric | GMRES (robust, memory-hungry) or BiCGSTAB (cheap, erratic) |

**Preconditioning.** Solve \(\mathbf{M}^{-1}\mathbf{A}\mathbf{x} = \mathbf{M}^{-1}\mathbf{b}\) with \(\mathbf{M}\approx\mathbf{A}\) cheap to invert:

- **Jacobi / diagonal** — nearly free, helps only with poor scaling.
- **ILU(k)** — good general-purpose, tuning via fill level; not naturally parallel.
- **Algebraic multigrid (AMG)** — near-optimal for elliptic operators, built from the matrix alone.
- **Block / physics-based** (e.g. SIMPLE-type for Navier–Stokes) — usually beats generic options when the block structure is known.

**Multigrid.** Rests on one observation: simple relaxation (Jacobi, Gauss–Seidel) kills high-frequency error fast and low-frequency error not at all. So smooth, restrict the residual to a coarser grid where the remaining error looks high-frequency, solve there, prolongate the correction back.

\[
\text{V-cycle cost} \approx 2\times\text{fine-grid work},
\qquad
\text{convergence factor} \sim 0.1\ \text{per cycle, independent of } N
\]

Grid-independent convergence is the property that matters: 10 cycles at \(10^6\) unknowns and 10 cycles at \(10^9\).

## Mental model

Think of the error as a superposition of wavelengths. Relaxation is a local averaging operation, so it can only see and damp wiggles comparable to the stencil — it flattens short wavelengths quickly and barely touches long ones. Multigrid's insight is that a long wavelength on a fine grid *is* a short wavelength on a coarse grid. Move it to where it can be seen.

Krylov methods build a polynomial in \(\mathbf{A}\) applied to the initial residual, and implicitly search for the polynomial that is smallest on the spectrum. If the eigenvalues are spread out, no low-degree polynomial can be small everywhere on them — which is exactly why ill-conditioning costs iterations, and why clustering helps more than shrinking \(\kappa\).

## Numerics / practice

- **Measure iterations against problem size.** Growing iteration counts mean the preconditioner is not scalable, and no amount of hardware will fix it.
- **Budget the preconditioner.** A setup that halves iterations but triples per-iteration cost is a loss. Compare wall-clock, not iterations.
- **Use relative residual with a sensible norm**, and report the criterion. `rtol=1e-6` on an unscaled system can mean anything.
- **Reuse preconditioners** across timesteps or Newton iterations where the matrix changes slowly — often the single biggest speedup available.

??? warning "Failure modes"
    **Residual read as error.** \(\|\mathbf{r}\| = \|\mathbf{b}-\mathbf{A}\mathbf{x}\|\) small implies \(\|\mathbf{e}\| \le \kappa\|\mathbf{r}\|/\|\mathbf{A}\|\) — at \(\kappa=10^8\) a residual of \(10^{-10}\) permits an error of \(10^{-2}\). The most common false confidence in numerical work.

    **CG on a non-SPD matrix.** It may run, and even appear to reduce something, while converging to nothing meaningful. Convection terms and most upwind discretizations are nonsymmetric. Check symmetry before choosing CG.

    **GMRES restart stagnation.** GMRES(m) discards the Krylov space every \(m\) iterations. On a hard problem, convergence flatlines completely after the first restart. Symptom: residual dropping nicely then going horizontal at a fixed value. Fix: larger \(m\), a better preconditioner, or a flexible variant.

    **Multigrid on anisotropic problems.** Standard coarsening assumes error is smooth in all directions equally. On high-aspect-ratio boundary-layer cells it is smooth along the cell and rough across, so coarsening in both directions fails. Symptom: convergence factor degrading from 0.1 towards 1 in exactly the stretched region. Fix: semi-coarsening or line relaxation.

    **BiCGSTAB breakdown.** Erratic, non-monotone residual histories and occasional hard breakdown. Cheap when it works; if the residual is bouncing by orders of magnitude, switch to GMRES rather than tightening the tolerance.

    **Ignoring the null space.** An all-Neumann Poisson problem is singular up to a constant. Krylov methods wander in the null direction and may report convergence on an inconsistent system. Pin a value or project the constant out, and check the right-hand side is compatible.

    **Tolerance tighter than the discretization error.** Solving to \(10^{-12}\) when the truncation error is \(10^{-4}\) burns iterations for nothing.

    <!-- Add your own here. -->

## Worked example

Why iteration counts, not matrix size, are the thing to watch:

```python
import numpy as np

for n in (32, 64, 128, 256):
    h = 1.0 / (n + 1)
    # 1D Poisson eigenvalues: 4/h^2 * sin^2(k*pi*h/2)
    k = np.arange(1, n + 1)
    lam = 4.0 / h**2 * np.sin(k * np.pi * h / 2.0)**2
    kappa = lam.max() / lam.min()
    cg_iters = 0.5 * np.sqrt(kappa) * np.log(2 / 1e-6)
    print(f"n={n:4d}  kappa={kappa:.3e}  CG iterations ~ {cg_iters:.0f}")
```

```
n=  32  kappa=4.407e+02  CG iterations ~ 152
n=  64  kappa=1.712e+03  CG iterations ~ 300
n= 128  kappa=6.744e+03  CG iterations ~ 596
n= 256  kappa=2.677e+04  CG iterations ~ 1187
```

Iterations double with each refinement — \(O(h^{-1})\), exactly as \(\sqrt{\kappa}\) predicts. Multigrid preconditioning flattens this to a constant, which is the whole reason it exists.

## Connections

- [Mathematical methods](math-methods.md) — conditioning, and where it comes from.
- [Numerical methods](numerical-methods.md) — the discretizations that produce these matrices.
- [Fluids › Incompressible flow](../fluids/incompressible.md) — the pressure Poisson solve as the dominant cost.
- [Fluids › Meshing](../fluids/cfd/meshing.md) — aspect ratio as a solver problem.

## Sources

- Saad, *Iterative Methods for Sparse Linear Systems*.
- Briggs, Henson & McCormick, *A Multigrid Tutorial* — short and genuinely tutorial.
- Trefethen & Bau, *Numerical Linear Algebra*.
- Archive: see the [course archive](../resources/course-archive.md).
