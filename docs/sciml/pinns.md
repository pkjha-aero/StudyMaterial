---
title: Physics-informed neural networks
status: working
tags: [pillar-9, sciml, neural-networks, inverse-problems, extrapolation]
updated: 2026-09-26
---

# Physics-informed neural networks

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - A PINN represents the solution as a network and puts the **PDE residual in the loss**, evaluated by automatic differentiation. No mesh.
    - **For forward problems on standard PDEs, a conventional solver is usually faster and more accurate.** PINNs earn their place on inverse problems and on data assimilation into physics.
    - **Loss balancing is the central practical difficulty.** Residual, boundary and data terms have different scales and gradients.
    - **Stiff, multiscale and advection-dominated problems are where PINNs fail**, and they fail by converging smoothly to a wrong answer.
    - Spectral bias makes networks learn low frequencies first — which is exactly wrong for sharp fronts.

## Key results

**The formulation.** Represent \(u(x,t)\approx u_\theta(x,t)\) and minimise:

<div class="result" markdown>

\[
\mathcal{L} = \underbrace{\lambda_r\frac{1}{N_r}\sum_{i}\left|\mathcal{N}[u_\theta](x_i,t_i)\right|^2}_{\text{PDE residual}}
+ \underbrace{\lambda_b\frac{1}{N_b}\sum_{j}\left|u_\theta - g\right|^2}_{\text{boundary/initial}}
+ \underbrace{\lambda_d\frac{1}{N_d}\sum_{k}\left|u_\theta - u^{\text{obs}}\right|^2}_{\text{data}}
\]

</div>

Derivatives in \(\mathcal{N}\) come from automatic differentiation of the network, exactly — no discretization error in the derivatives themselves.

**Where PINNs are genuinely competitive:**

| Problem type | PINN vs conventional |
|---|---|
| Forward, standard PDE, simple domain | **conventional wins** — faster, error bounds, mature |
| Inverse: infer coefficients from sparse data | **PINN competitive** — the data term is natural |
| Data assimilation into physics | **PINN competitive** |
| High-dimensional PDEs (\(d\gtrsim4\)) | **PINN wins** — no mesh to build |
| Irregular geometry, no mesh available | PINN attractive |
| Stiff / multiscale / shocks | conventional wins decisively |

The honest summary: PINNs are a method for problems where you have physics *and* data and no clean way to combine them — not a replacement for a solver.

**Loss balancing.** The terms have different magnitudes and gradient scales, and a fixed \(\lambda\) usually lets one dominate. Approaches:

- **Hard-constrained boundaries**: write \(u_\theta = g + B(x)\,\mathcal{NN}(x)\) where \(B\) vanishes on the boundary. Removes the boundary loss term entirely and is the most robust fix available.
- **Gradient-based adaptive weights** (learning-rate annealing): rescale \(\lambda\) from the ratio of gradient norms.
- **NTK-based weighting**: balance by the neural tangent kernel eigenvalues.
- **Causal / time-marching training**: weight early times first, so the network does not fit late times before the early solution is right.

**Spectral bias.** Networks fit low frequencies first and high frequencies slowly or never. For a smooth diffusion problem this is harmless; for a sharp front or a high-wavenumber solution it means the answer is systematically over-smoothed. Fourier feature embeddings \(\gamma(x)=[\sin(2\pi Bx),\cos(2\pi Bx)]\) mitigate it by presenting high frequencies to the network directly.

**Collocation points.** Sampled in the domain, and their placement matters as much as mesh placement does for a solver. Adaptive sampling — adding points where the residual is large (RAR) — is a standard and effective improvement.

## Mental model

A PINN turns solving a PDE into fitting a function that happens to satisfy the PDE. That is a different optimisation problem than the one a solver poses, with a different failure surface — and critically, **a low loss does not mean a small error**.

A conventional solver has convergence theory: refine, and the error decreases at a known rate. A PINN has a non-convex optimisation whose loss can plateau at a solution satisfying the PDE almost everywhere while being wrong where it matters. There is no analogue of grid convergence, which is why verification for PINNs is genuinely harder — see [V&V](../foundations/verification-validation.md).

## Numerics / practice

- **Hard-constrain boundary conditions** wherever the geometry permits. This eliminates the most common tuning problem outright.
- **Nondimensionalise first.** Terms spanning many orders of magnitude make the residual loss dominated by one of them.
- **Use adaptive collocation sampling**; uniform sampling wastes points in easy regions.
- **Always compare against a reference solution** on a case where one exists, before trusting the method on one where it does not.

??? warning "Failure modes"
    **Low loss, wrong solution.** The defining PINN failure. The residual can be small on the collocation points while the solution is badly wrong between them, or converged to a different branch. Unlike a solver, there is no refinement study that bounds the error. Always validate against a reference.

    **Trivial solution for a homogeneous problem.** With homogeneous boundary conditions and no data term, \(u\equiv0\) satisfies the PDE residual and the boundary loss exactly. The optimizer finds it immediately. Symptom: loss plunges to near machine zero within a few hundred iterations, which reads like success.

    **Loss terms out of balance.** If the residual term is \(10^4\) times the boundary term, boundary conditions are effectively unenforced and the network converges to some other solution of the same PDE. Symptom: a smooth, plausible field that does not match the boundary data.

    **Stiff or multiscale problems.** Boundary layers, reaction-diffusion with disparate timescales, high Reynolds number. Spectral bias plus the imbalance between terms makes these fail reliably. This is not a tuning issue; it is the method's domain of validity.

    **Advection-dominated and shocked problems.** PINNs smooth discontinuities, because a network with smooth activations is a smooth function and the residual at a discontinuity is undefined anyway. Weak/variational formulations help; the vanilla method does not.

    **Long time integration.** Training over a long time window with uniform weighting lets the network fit late times before the early solution is correct, and errors propagate backwards through the optimisation. Causal weighting or sequential time-windowing is needed.

    **Benchmarked only against easy cases.** Much of the published PINN literature evaluates on 1D Burgers and 2D Poisson, where conventional solvers take milliseconds. Timing comparisons that omit the solver baseline overstate the case considerably.

    <!-- Add your own here. -->

## Worked example

Spectral bias, in the quantity that causes it — the residual's sensitivity to frequency:

```python
import numpy as np

# For u = sin(k*pi*x), the Laplacian scales as k^2, so the PDE residual
# loss for an error of fixed amplitude scales as k^4.
print(f"{'k':>4} {'|u|':>6} {'|u_xx|':>10} {'residual weight':>17}")
for k in (1, 2, 4, 8, 16):
    amp_u = 1.0
    amp_uxx = (k * np.pi)**2
    print(f"{k:4d} {amp_u:6.1f} {amp_uxx:10.1f} {amp_uxx**2 / (np.pi**4):17.1f}")
```

```
   k    |u|     |u_xx|   residual weight
   1    1.0        9.9               1.0
   2    1.0       39.5              16.0
   4    1.0      157.9             256.0
   8    1.0      631.7            4096.0
  16    1.0     2526.6           65536.0
```

A mode-16 error contributes 65,536 times more to a second-order residual loss than a mode-1 error of the same amplitude. That should make high frequencies *easier* to fit — and yet networks learn them last, because the gradient descent dynamics are governed by the neural tangent kernel spectrum, which decays with frequency faster than the residual weighting grows. Spectral bias wins, which is precisely why Fourier features are needed rather than just reweighting the loss.

## Connections

- [Neural operators](neural-operators.md) — learning the solution *map* instead of one solution.
- [Surrogates and ROM](surrogates-rom.md) — the projection-based alternative.
- [Hybrid coupling](hybrid-coupling.md) — ML inside a conventional solver.
- [Foundations › V&V](../foundations/verification-validation.md) — why PINN verification is hard.

## Sources

- Raissi, Perdikaris & Karniadakis (2019), *Physics-informed neural networks*.
- Wang, Teng & Perdikaris (2021), *Understanding and mitigating gradient pathologies in PINNs*.
- Krishnapriyan et al. (2021), *Characterizing possible failure modes in physics-informed neural networks*.
