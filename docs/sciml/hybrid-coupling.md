---
title: Hybrid physics-ML coupling
status: working
tags: [pillar-9, sciml, closures, stability, differentiable-simulation]
updated: 2026-09-26
---

# Hybrid physics-ML coupling

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - Put ML **inside** the solver — a learned closure, correction or sub-model — and keep the conservation and numerics you trust.
    - **A posteriori stability is the problem.** A closure with excellent offline accuracy can destabilise the coupled run.
    - **Train in the loop, not offline**, where you can: differentiable solvers let the learned term see its own downstream consequences.
    - **Embed known invariances** — Galilean, rotational, realisability — rather than hoping they are learned.
    - Know what happens when the model is asked something outside its training distribution, because in a coupled run it certainly will be.

## Key results

**Where ML can sit in a solver:**

<div class="result" markdown>

| Placement | Example | Risk |
|---|---|---|
| Closure term | subgrid stress, RANS correction | stability, realisability |
| Source term | chemistry, microphysics | stiffness, positivity |
| Correction to a coarse solve | learned defect correction | drift |
| Preconditioner / initial guess | learned multigrid smoother | **none — worst case is slow** |
| Full surrogate of a component | radiation, thermodynamics lookup | consistency with the rest |

</div>

The preconditioner row is worth noting: ML that only *accelerates* a convergent iteration cannot corrupt the answer, because the residual still has to be driven to zero. That makes it the safest place to start, and it is under-used relative to closure learning.

**A priori versus a posteriori.** A closure trained offline to match filtered DNS stresses is evaluated *a priori* by correlation with the true stress. Plugged into a running solver, it is evaluated *a posteriori* by whether the simulation is right and stable. **These correlate poorly.** Models with 0.9 a priori correlation routinely diverge a posteriori, and models with modest correlation can perform well — because what matters is the divergence of the stress and its energy transfer, not the stress itself.

**Why closures destabilise.** A physical subgrid model is dissipative by construction: it removes energy from resolved scales. A learned model fits the *mean* behaviour, including the backscatter events where energy flows up-scale. Those events are real, but a model that reproduces them without the compensating physics injects energy with no bound, and the simulation blows up. Standard mitigations:

- **Clipping** the eddy viscosity to be non-negative (crude, effective, sacrifices backscatter).
- **Projection** onto a realisable set (the stress tensor must stay positive semi-definite).
- **Structural constraints** in the architecture that guarantee net dissipation.

**Differentiable simulation.** If the solver is written in a differentiable framework, the closure can be trained through \(n\) solver steps:

\[
\mathcal{L} = \sum_{k=1}^{n}\left\|u^{k}_{\text{coarse+ML}} - u^{k}_{\text{filtered DNS}}\right\|^2
\]

The gradient flows through the numerics, so the learned term is optimised for its effect on the trajectory rather than for pointwise stress accuracy. This directly targets the a priori/a posteriori gap and is the most important development in the area. It inherits the chaotic-adjoint limit from [adjoints](../foundations/optimization-adjoints.md): the gradient is only usable over short windows.

**Invariance embedding.** A Galilean-invariant closure must depend on velocity *gradients*, not velocities. A rotationally invariant one should be built from the tensor invariants. Constructing the model from an invariant basis — as the tensor-basis neural network does for Reynolds stress — guarantees the symmetry instead of hoping for it, and cuts the data needed substantially.

## Mental model

The solver is a trusted machine with a broken part. Hybrid modelling replaces the part, not the machine — conservation, boundary conditions and time integration remain exactly as verified.

The catch is that the replacement part sits inside a feedback loop. Its output changes the state, which changes its next input. Offline training optimises the part in isolation; the loop is what actually runs. Every characteristic failure here is a consequence of that gap, and every good practice — in-the-loop training, stability constraints, invariance embedding — is a way of closing it.

## Numerics / practice

- **Start with an accelerator, not a closure.** A learned initial guess or preconditioner cannot make the answer wrong.
- **Always evaluate a posteriori**, on runs long enough to expose drift. A priori metrics are a screening tool at best.
- **Enforce realisability and positivity explicitly** in code, not in the loss.
- **Instrument the out-of-distribution case**: log when the closure's inputs leave the training envelope, and decide in advance whether to fall back to a physical model.

??? warning "Failure modes"
    **A priori accuracy taken as evidence.** The most consequential mistake in this area. High correlation with true subgrid stress does not predict coupled performance, and the literature is full of models that never ran in a solver. If a closure has not been run a posteriori, it has not been evaluated.

    **Energy injection and blow-up.** A learned closure that occasionally predicts negative dissipation adds energy the physics does not supply. In a long run the resolved scales gain energy until the solver fails, often after a long apparently-healthy period. Symptom: stable for thousands of steps, then rapid divergence — which reads like a numerical bug rather than a model one.

    **Out-of-distribution inputs during the run.** A coupled simulation visits states no offline dataset contained, especially after the closure has already altered the trajectory. The model extrapolates, the trajectory moves further out, and the feedback is self-reinforcing.

    **Conservation broken by the learned term.** A closure added as a source without a corresponding flux form violates the conservation the rest of the solver maintains exactly. The drift is slow and easy to miss over short tests.

    **Invariance not embedded.** A closure taking raw velocity components learns the training frame. Symptom: performance that changes when the domain is translated, rotated or the flow direction reversed — physically impossible, and a clear diagnostic.

    **Resolution dependence unaddressed.** A subgrid model is specific to a filter width. Deployed at a different grid spacing than trained, it applies the wrong amount of dissipation. The model should take \(\Delta\) as an input, and be trained across a range of it.

    **Speedup quoted without the training cost, or without matched accuracy.** A hybrid model that runs 50× faster than DNS but only matches a much cheaper LES is not a 50× speedup. Compare against the cheapest conventional method that reaches the same accuracy.

    <!-- Add your own here. -->

## Worked example

Why occasional negative dissipation is fatal rather than merely inaccurate:

```python
import numpy as np
rng = np.random.default_rng(0)

n_steps, dt = 20_000, 0.01
E_phys = E_ml = 1.0
# a physical closure is strictly dissipative; a learned one is right on average
# but has a small negative tail
for _ in range(n_steps):
    eps = rng.normal(0.10, 0.05)            # learned dissipation estimate
    E_phys *= (1 - dt * max(eps, 0.0))      # clipped: never adds energy
    E_ml   *= (1 - dt * eps)                # unclipped: sometimes adds
    E_phys += dt * 0.10 * 1.0               # steady forcing
    E_ml   += dt * 0.10 * 1.0

print(f"mean dissipation      : 0.100  (std 0.05, ~2.3% of samples negative)")
print(f"energy, clipped model : {E_phys:.4f}")
print(f"energy, unclipped     : {E_ml:.4f}")
```

```
mean dissipation      : 0.100  (std 0.05, ~2.3% of samples negative)
energy, clipped model : 1.0113
energy, unclipped     : 1.0162
```

Over 20,000 steps both stay bounded here, because the negative excursions are small and rare and the linear feedback is weak. That is the *benign* regime — and it is why the failure is so treacherous: in a real nonlinear solver the energy gained feeds larger gradients, which feed larger closure outputs, and the same 2% negative tail becomes a divergence. A short test showing bounded energy is not evidence of stability.

## Connections

- [PINNs](pinns.md) · [Neural operators](neural-operators.md) · [GNNs on meshes](gnn-meshes.md) — the alternatives to coupling.
- [Fluids › LES](../fluids/turbulence/les.md) — the closure being replaced.
- [Fluids › RANS](../fluids/turbulence/rans.md) — realisability and the Boussinesq limits.
- [Foundations › Optimization and adjoints](../foundations/optimization-adjoints.md) — differentiable solvers and the chaotic limit.

## Sources

- Duraisamy, Iaccarino & Xiao (2019), *Turbulence modeling in the age of data*.
- Ling, Kurzawski & Templeton (2016), *Reynolds-averaged turbulence modelling using deep neural networks with embedded invariance*.
- Um et al. (2020), *Solver-in-the-loop*.
- Beck & Kurz (2021), *A perspective on machine learning methods in turbulence modeling*.
