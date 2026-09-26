---
title: Scientific ML
status: working
tags: [pillar-9, sciml]
---

# Scientific ML

<span class="status status-working">working</span>
<span class="pillar">pillar 9</span>

The bridge between the two halves of this site: learning that respects, replaces, or
accelerates part of a solver.

## Pages

| Page | Covers |
|---|---|
| [Surrogates and reduced-order models](surrogates-rom.md) | POD, DMD, Galerkin projection, hyper-reduction, the \(n\)-width barrier |
| [Physics-informed neural networks](pinns.md) | Residual losses, loss balancing, spectral bias, where PINNs actually win |
| [Neural operators](neural-operators.md) | FNO, DeepONet, amortisation, mode truncation, rollout |
| [Graph networks on meshes](gnn-meshes.md) | Message passing as a learned stencil, locality, rollout stability |
| [Hybrid physics-ML coupling](hybrid-coupling.md) | Learned closures, a priori vs a posteriori, differentiable solvers |

## Choosing between them

| You have | You want | Reach for |
|---|---|---|
| Many solves of one parametric family | Fast repeated queries | [Neural operator](neural-operators.md) or [ROM](surrogates-rom.md) |
| Physics and sparse data, unknown coefficients | The coefficients | [PINN](pinns.md) |
| An unstructured mesh and trajectories | A learned simulator | [Mesh GNN](gnn-meshes.md) |
| A working solver with one weak sub-model | A better sub-model | [Hybrid coupling](hybrid-coupling.md) |
| One solve | The answer | **a conventional solver** |

That last row is not a joke. For a single forward solve of a standard PDE, a conventional
method is faster, more accurate, and comes with convergence theory. Every method on these
pages earns its keep through *amortisation* (many queries), *inverse problems* (data plus
physics), or *closure* (a gap the physics leaves open).

## The theme that runs through every page

**All of these methods interpolate over a distribution they were trained on, and none of
them slow down when asked something outside it.** A solver given an unreasonable input
either fails to converge or produces a visibly wrong field. A learned model returns a
fast, smooth, confident answer regardless.

That asymmetry is why the discipline here is different from the rest of the site:
verification cannot rely on refinement, so it has to rely on knowing and recording the
training distribution, testing a posteriori rather than offline, and instrumenting the
out-of-distribution case at run time.

## Connections

- [Fluids › Turbulence](../fluids/turbulence/index.md) — where closures are needed.
- [Foundations › V&V](../foundations/verification-validation.md) — and why it is harder here.
- [Foundations › UQ](../foundations/uncertainty-quantification.md) — the workloads that make surrogates pay.
- [Deep Learning](../dl/index.md) · [Machine Learning](../ml/index.md) — the underlying methods.
