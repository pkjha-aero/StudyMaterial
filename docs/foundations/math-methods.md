---
title: Mathematical methods
status: solid
tags: [pillar-2, foundations, spectral-methods]
updated: 2026-09-26
---

# Mathematical methods

<span class="status status-solid">solid</span>
<span class="pillar">pillar 2 &middot; Mathematical methods</span>

!!! abstract "In one minute"
    - **PDE type decides everything downstream**: how information travels, how many boundary conditions you may impose, and which discretization is admissible.
    - Hyperbolic propagates at finite speed, parabolic smooths instantly, elliptic couples the whole domain at once. Most real systems are mixed.
    - **Well-posedness** is existence, uniqueness *and* continuous dependence on data. The third is the one numerics destroys.
    - The **condition number** bounds how much input error your answer can amplify. It is a property of the problem, not of the algorithm.
    - **Singular perturbations** — a small parameter multiplying the highest derivative — produce boundary layers, and naive expansion fails on them.

## Key results

**Second-order PDE classification.** For \(A\phi_{xx} + B\phi_{xy} + C\phi_{yy} + \dots = 0\):

<div class="result" markdown>

| Discriminant | Type | Example | Information | BCs |
|---|---|---|---|---|
| \(B^2 - 4AC > 0\) | hyperbolic | wave, Euler | finite speed, along characteristics | initial + inflow |
| \(B^2 - 4AC = 0\) | parabolic | heat, boundary layer | infinite speed, smoothing | initial + all boundaries |
| \(B^2 - 4AC < 0\) | elliptic | Laplace, pressure Poisson | instantaneous, global | all boundaries |

</div>

For a first-order system \(\mathbf{u}_t + \mathbf{A}\mathbf{u}_x = 0\), the type is set by the eigenvalues of \(\mathbf{A}\): all real and distinct means hyperbolic; complex means elliptic.

**Number of boundary conditions.** For a hyperbolic system, impose exactly as many conditions at a boundary as there are characteristics *entering* the domain there. Over-specifying makes the problem ill-posed; under-specifying leaves it undetermined. This is not a numerical convention — it is the mathematics.

**Well-posedness (Hadamard).** A problem is well posed if a solution exists, is unique, and depends continuously on the data. Backward heat conduction fails the third: arbitrarily small data perturbations produce arbitrarily large solution changes. Every inverse problem is ill-posed in this sense, which is why regularization exists.

**Condition number.** For \(\mathbf{A}\mathbf{x} = \mathbf{b}\):

\[
\kappa(\mathbf{A}) = \|\mathbf{A}\|\,\|\mathbf{A}^{-1}\| = \frac{\sigma_{\max}}{\sigma_{\min}},
\qquad
\frac{\|\delta\mathbf{x}\|}{\|\mathbf{x}\|} \le \kappa(\mathbf{A})\frac{\|\delta\mathbf{b}\|}{\|\mathbf{b}\|}
\]

A rule of thumb: you lose about \(\log_{10}\kappa\) decimal digits. At \(\kappa \sim 10^{16}\) in double precision, nothing is left.

**SVD** \(\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^{\mathsf T}\) — the decomposition worth reaching for first. It gives rank, condition number, the best low-rank approximation (Eckart–Young), the pseudo-inverse, and the numerically stable least-squares solution.

**Matched asymptotic expansions.** For \(\epsilon y'' + y' + y = 0\), \(\epsilon \ll 1\): the outer solution drops the \(\epsilon\) term and cannot satisfy both boundary conditions. Rescale \(x = \epsilon X\) near the boundary to recover the inner solution, then match in the overlap region. The boundary layer thickness is set by the rescaling that balances the dominant terms — \(\delta \sim \epsilon\) here, \(\delta \sim \mathrm{Re}^{-1/2}\) for the Navier–Stokes boundary layer.

**Index notation** saves more errors than it costs to learn. \(\partial_i u_i\) is divergence, \(\epsilon_{ijk}\partial_j u_k\) is curl, repeated indices sum. The identity worth memorising:

\[
(\mathbf{u}\cdot\nabla)\mathbf{u} = \nabla\left(\tfrac{1}{2}|\mathbf{u}|^2\right) - \mathbf{u}\times(\nabla\times\mathbf{u})
\]

## Mental model

Ask where information can go. In an elliptic problem it goes everywhere instantly, so you need a global solve and boundary data all round. In a hyperbolic problem it travels along characteristics at finite speed, so there are regions the solution cannot yet know about — which is exactly what an explicit marching scheme exploits, and what the CFL condition encodes.

Conditioning is a separate question: not *where* information travels but *how much it is amplified*. An ill-conditioned problem is one where the answer is genuinely hypersensitive to the input. No algorithm fixes that; it is a property of the question you asked.

## Numerics / practice

- **Classify before discretizing.** A scheme appropriate for one type is usually unstable or inconsistent for another. Central differencing is natural for elliptic and wrong for strongly hyperbolic problems.
- **Count your boundary conditions** against the characteristics, especially at outflow.
- **Compute \(\kappa\)** (or estimate it) for any linear system you are about to trust. `numpy.linalg.cond` is cheap on small problems and `scipy.sparse.linalg` has estimators for large ones.
- **Prefer SVD or QR to the normal equations** for least squares — forming \(\mathbf{A}^{\mathsf T}\mathbf{A}\) squares the condition number.

??? warning "Failure modes"
    **Misclassifying a mixed-type system.** Transonic flow is elliptic in the subsonic region and hyperbolic in the supersonic one, with the type changing across the sonic line. A scheme built for one type produces nonsense in the other region, and the symptom appears far from the actual sonic line.

    **Over-specified outflow boundary.** Imposing both pressure and velocity at a subsonic outlet over-determines the problem. Symptom: a persistent reflection or a solution that will not converge, with residuals concentrated at the boundary.

    **Normal equations for least squares.** \(\kappa(\mathbf{A}^{\mathsf T}\mathbf{A}) = \kappa(\mathbf{A})^2\), so a mildly ill-conditioned fit becomes unusable. Symptom: coefficients that change wildly with tiny data changes. Fix: QR or SVD.

    **Small residual read as small error.** \(\|\mathbf{b}-\mathbf{A}\mathbf{x}\|\) small does not mean \(\|\mathbf{x}-\mathbf{x}^*\|\) small — the gap is exactly \(\kappa\). This is the most common misplaced confidence in computational work.

    **Regular perturbation on a singular problem.** Expanding in \(\epsilon\) when \(\epsilon\) multiplies the highest derivative loses a boundary condition and misses the boundary layer entirely. The symptom is an expansion that cannot satisfy all the boundary data — which is the signal to rescale, not to add more terms.

    **Assuming symmetry or positive-definiteness.** Convection terms are not symmetric. Applying CG to a non-SPD system may converge to something, and it will not generally be the solution.

    <!-- Add your own here. -->

## Worked example

Conditioning, and why the normal equations are a trap:

```python
import numpy as np

n = 12
A = np.vander(np.linspace(0, 1, 40), n)        # polynomial design matrix
print(f"cond(A)     = {np.linalg.cond(A):.3e}")
print(f"cond(A^T A) = {np.linalg.cond(A.T @ A):.3e}")
print(f"digits lost, normal equations: {np.log10(np.linalg.cond(A.T @ A)):.1f} of 16")
```

```
cond(A)     = 1.179e+08
cond(A^T A) = 1.343e+16
digits lost, normal equations: 16.1 of 16
```

The design matrix is merely awkward; its normal-equations form has almost no accuracy left in double precision.

## Connections

- [Numerical methods](numerical-methods.md) — turning these PDEs into discrete systems.
- [Linear solvers](linear-solvers.md) — where conditioning becomes a runtime cost.
- [Fluids › Governing equations](../fluids/governing-equations.md) — PDE type in practice.
- [Fluids › Compressible flow](../fluids/compressible.md) — characteristics and boundary-condition counting.

## Sources

- Strang, *Computational Science and Engineering*.
- Trefethen & Bau, *Numerical Linear Algebra* — conditioning and SVD, exceptionally clear.
- Bender & Orszag, *Advanced Mathematical Methods* — asymptotics and matched expansions.
- Archive: see the [course archive](../resources/course-archive.md).
