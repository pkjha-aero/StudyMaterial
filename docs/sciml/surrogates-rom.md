---
title: Surrogates and reduced-order models
status: working
tags: [pillar-9, sciml, surrogates, spectral-methods, extrapolation]
updated: 2026-09-26
---

# Surrogates and reduced-order models

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - A surrogate replaces an expensive solver with a cheap approximation. The question is always **what it is allowed to be asked**.
    - **POD is the SVD of your snapshots** — optimal linear subspace, and its singular value decay tells you whether reduction is even possible.
    - **Advection-dominated problems reduce badly.** Slowly decaying singular values are the diagnostic, and no amount of modes fixes it.
    - **DMD extracts dynamics**, not just structure: modes with growth rates and frequencies.
    - Projection-based ROMs can be **unstable even when the full-order model is not** — reduction does not preserve stability.

## Key results

**POD / PCA on snapshots.** Assemble snapshot matrix \(X \in \mathbb{R}^{n\times m}\) (state size \(n\), \(m\) snapshots) and take the SVD:

<div class="result" markdown>

\[
X = U\Sigma V^{\mathsf T},
\qquad
x(t) \approx \sum_{i=1}^{r} a_i(t)\,u_i,
\qquad
E(r) = \frac{\sum_{i\le r}\sigma_i^2}{\sum_i \sigma_i^2}
\]

</div>

\(U_r\) is the optimal rank-\(r\) subspace in the \(L_2\) sense (Eckart–Young). The **singular value decay is the first thing to plot**: fast decay means the dynamics live on a low-dimensional manifold and reduction will work; slow decay means it will not.

**Galerkin projection.** Substitute \(x = U_r a\) into \(\dot x = f(x)\) and project:

\[
\dot a = U_r^{\mathsf T} f(U_r a)
\]

For a quadratic nonlinearity (as in Navier–Stokes) this gives precomputable tensors and genuine speedup. For a general nonlinearity it does not — evaluating \(f\) still costs \(O(n)\), which is what **hyper-reduction** (DEIM, ECSW) exists to fix: evaluate \(f\) at a small set of sampled points and interpolate.

**DMD.** Fit a best-fit linear operator between consecutive snapshots:

\[
X' \approx A X,
\qquad
A = X' X^{\dagger},
\qquad
A\phi_i = \lambda_i\phi_i
\]

Each mode has a growth rate \(\log|\lambda_i|/\Delta t\) and a frequency \(\arg(\lambda_i)/\Delta t\). Unlike POD, DMD modes are **monochromatic** — one frequency each — which is why DMD is the tool when you want to identify and separate dynamic mechanisms rather than just compress.

**Method comparison:**

| Method | Gives | Linear? | Good for |
|---|---|---|---|
| POD | optimal energy basis | linear subspace | compression, Galerkin ROM |
| DMD | modes with dynamics | linear operator | mechanism identification, short-term forecast |
| Autoencoder | nonlinear manifold | no | advection-dominated, where POD fails |
| Gaussian process | interpolant + uncertainty | no | few parameters, expensive samples |
| Neural network | general map | no | many parameters, many samples |

**The Kolmogorov \(n\)-width barrier.** For a travelling wave, no linear subspace of modest dimension captures the solution — a moving front needs many Fourier-like modes. This is a theorem about linear reduction, not a numerical difficulty, and it is why autoencoders and registration/transport-based methods exist for advective problems.

**Gaussian process surrogates** give a predictive variance alongside the mean, which makes them the natural choice for expensive-sample parameter studies and for adaptive sampling — see [UQ](../foundations/uncertainty-quantification.md).

## Mental model

A high-dimensional simulation usually explores a much smaller set of states than its degrees of freedom allow. POD finds the best flat slice through that set; an autoencoder finds a curved one. The reduction works to the extent the states really do cluster on such a surface.

That is also the precise statement of when it fails. A travelling front visits genuinely new regions of state space as it moves, so there is no low-dimensional flat surface containing its trajectory. The singular values say so before you build anything.

## Numerics / practice

- **Plot the singular value spectrum first**, on a log scale. It is a five-minute check that decides whether the project is feasible.
- **Sample the snapshots across the parameter range** you intend to query. A ROM built at one Reynolds number is valid at that Reynolds number.
- **Subtract the mean** before POD unless you have a reason not to; otherwise the first mode is the mean and the energy fractions mislead.
- **Check ROM stability explicitly** by long-time integration, not just by reconstruction error on the training snapshots.

??? warning "Failure modes"
    **Applying POD to an advection-dominated problem.** Slowly decaying singular values, and a ROM that needs hundreds of modes to be accurate — at which point it is not reduced. The mistake is treating this as a tuning problem. It is the Kolmogorov \(n\)-width barrier, and the fix is a different class of method.

    **Unstable Galerkin ROM.** Truncating the modes removes the small scales that drained energy in the full system, so energy accumulates in the retained modes and the ROM blows up — even though the full-order model is stable. Symptom: excellent short-time accuracy, divergence at long time. Fixes: closure terms, stabilising projection (Petrov–Galerkin), or retaining more modes.

    **Reconstruction error mistaken for predictive error.** Projecting training snapshots onto their own POD basis always reconstructs well. That measures the basis, not the ROM. The real test is integrating the reduced dynamics forward and comparing with a held-out full-order run.

    **Extrapolating outside the training parameter range.** A surrogate interpolates the data it saw. Queried at a Reynolds number, geometry or forcing outside that envelope it returns a confident, unconstrained answer. This is the central risk of surrogates in engineering use.

    **Nonlinear term without hyper-reduction.** The ROM has \(r\) degrees of freedom but still evaluates the nonlinearity over all \(n\) points, so the speedup never materialises. Common and disappointing.

    **DMD on under-sampled dynamics.** DMD assumes the snapshot interval resolves the frequencies present. Under-sampling aliases them, and the identified growth rates are wrong in a way that looks physical.

    **Mean not subtracted.** The dominant "mode" is then the time-averaged field, the energy fractions are dominated by it, and mode-count decisions are made on a misleading spectrum.

    <!-- Add your own here. -->

## Worked example

Singular-value decay as the go/no-go test, on two fields that look equally simple:

```python
import numpy as np

nx, nt = 400, 400
x = np.linspace(0, 1, nx)
t = np.linspace(0, 1, nt)

# (a) standing oscillation: separable, low rank by construction
standing = np.outer(np.sin(np.pi * x), np.cos(6 * np.pi * t)) \
         + 0.4 * np.outer(np.sin(3 * np.pi * x), np.sin(4 * np.pi * t))

# (b) travelling front: same smoothness, not separable
front = np.array([np.tanh((x - 0.15 - 0.7 * ti) / 0.005) for ti in t]).T

for name, X in (("standing", standing), ("travelling front", front)):
    s = np.linalg.svd(X, compute_uv=False)
    e = np.cumsum(s**2) / np.sum(s**2)
    r = [int(np.searchsorted(e, q) + 1) for q in (0.90, 0.99, 0.999)]
    print(f"{name:18s} 90% -> {r[0]:3d} modes   99% -> {r[1]:3d}   99.9% -> {r[2]:3d}")
```

```
standing           90% ->   2 modes   99% ->   2   99.9% ->   2
travelling front   90% ->   4 modes   99% ->  17   99.9% ->  45
```

The standing pattern is rank 2 exactly, at every tolerance. The travelling front — no more complex to look at, and perfectly smooth — needs 17 modes for 99% and 45 for 99.9%, and the count keeps climbing as the front sharpens or the domain lengthens. There is no tolerance at which it becomes low-rank.

Ten minutes of SVD tells you which project you are on, and the third column is the one to read: a field whose mode count *grows* as you tighten the tolerance is not reducible by a linear basis.

## Connections

- [Neural operators](neural-operators.md) — learning the solution map instead of a basis.
- [PINNs](pinns.md) — the other way to embed physics.
- [Foundations › Math methods](../foundations/math-methods.md) — SVD and conditioning.
- [Foundations › UQ](../foundations/uncertainty-quantification.md) — GP emulators.
- [Fluids › Turbulence](../fluids/turbulence/index.md) — where POD originated.

## Sources

- Benner, Gugercin & Willcox (2015), *A survey of projection-based model reduction methods*.
- Kutz, Brunton, Brunton & Proctor, *Dynamic Mode Decomposition*.
- Brunton & Kutz, *Data-Driven Science and Engineering*.
