---
title: Neural operators
status: working
tags: [pillar-9, sciml, fno, deeponet, operator-learning]
updated: 2026-09-26
---

# Neural operators

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - A neural operator learns a **map between function spaces** — initial condition to solution, coefficient field to response — not a single solution.
    - Train once over a family of problems, then evaluate in milliseconds. That amortisation is the entire value proposition.
    - **FNO** performs global convolution in Fourier space, giving \(O(n\log n)\) cost and a degree of resolution independence.
    - **DeepONet** separates the input function (branch) from the query location (trunk), which makes arbitrary output locations natural.
    - **Resolution invariance is partial, not free** — it holds for the operator, not for features the training resolution never contained.

## Key results

**The object being learned.** Not \(u = f(x)\) but \(\mathcal{G}: a \mapsto u\), mapping an input *function* to a solution *function*:

<div class="result" markdown>

\[
\mathcal{G}^\dagger: \mathcal{A}\to\mathcal{U},
\qquad
\mathcal{G}_\theta \approx \mathcal{G}^\dagger,
\qquad
\min_\theta \mathbb{E}_{a\sim\mu}\left\|\mathcal{G}_\theta(a) - \mathcal{G}^\dagger(a)\right\|^2
\]

</div>

The expectation is over a **distribution of input functions** \(\mu\). That distribution is the operator's domain of validity, and it is the thing most often left unstated.

**Fourier Neural Operator.** Each layer applies a global kernel integral, implemented as a multiplication in Fourier space:

\[
v_{t+1}(x) = \sigma\left(W v_t(x) + \mathcal{F}^{-1}\left[R_\phi\cdot\mathcal{F}[v_t]\right](x)\right)
\]

with \(R_\phi\) a learned complex weight applied to the lowest \(k_{\max}\) modes. Truncating to \(k_{\max}\) modes is both the efficiency mechanism and the main limitation: **anything above the retained mode count is invisible to the operator**.

Cost per layer: \(O(n\log n)\) from the FFT, versus \(O(n^2)\) for a dense global kernel.

**DeepONet.** Universal approximation for operators, realised as two networks combined by an inner product:

\[
\mathcal{G}_\theta(a)(y) \approx \sum_{k=1}^{p} \underbrace{b_k(a(x_1),\dots,a(x_m))}_{\text{branch}}\cdot\underbrace{t_k(y)}_{\text{trunk}}
\]

The branch encodes the input function sampled at fixed sensors; the trunk encodes the query point. Because the trunk takes \(y\) as an argument, output can be evaluated at any location — no output grid required, which is a real advantage on irregular domains.

**Comparison:**

| | FNO | DeepONet |
|---|---|---|
| Input sampling | regular grid (natively) | fixed sensor locations |
| Output locations | same grid | arbitrary |
| Global receptive field | yes, by construction | via the branch |
| Resolution transfer | good within the mode budget | depends on trunk |
| Irregular geometry | needs Geo-FNO or a mapping | natural |

**Amortisation.** A conventional solver costs \(C_{\text{solve}}\) per query. An operator costs \(N C_{\text{solve}}\) to generate training data plus training, then \(\epsilon\) per query. It wins when the number of queries greatly exceeds \(N\) — design optimisation, UQ sampling, real-time control, ensemble forecasting. For a handful of solves it never pays back.

## Mental model

A conventional solver is an algorithm that answers one question at a time. A neural operator is a *compiled* approximation of the solver, over a family of questions you specify in advance by choosing the training distribution.

That framing makes the limits obvious. A compiled function is fast because the work was done ahead of time, on a particular set of inputs. Ask it something outside that set and it does not slow down and think — it returns a fast, confident, unconstrained answer. Speed and extrapolation risk are two sides of the same amortisation.

## Numerics / practice

- **Define and record the training distribution** — parameter ranges, forcing statistics, boundary types. It is the operator's specification.
- **Choose \(k_{\max}\) against the spectrum of your solutions**, not by default. Plot the energy above the cutoff.
- **Test at a different resolution** than trained, deliberately, to see where resolution transfer actually holds.
- **Roll out autoregressively and watch the error**, if you intend time stepping. Single-step error is not the relevant number.

??? warning "Failure modes"
    **Out-of-distribution input.** The operator interpolates over the training distribution of input functions. A different Reynolds number, a rougher coefficient field, a boundary condition type not sampled — the output is plausible and unconstrained. This is the dominant risk, and it is not detectable from the output alone.

    **Modes above \(k_{\max}\) silently discarded.** FNO truncates. Sharp fronts, shocks, and fine-scale turbulence live above the cutoff and are simply absent from the prediction — smoothed away with no error signal. Symptom: predictions that look good in bulk metrics and lack all the small-scale structure.

    **Autoregressive error accumulation.** Rolling the operator forward feeds its own output back in, and each step's output is slightly off-distribution for the next. Errors compound, often catastrophically after tens of steps. Single-step validation error says nothing about rollout stability. Mitigations: training on rolled-out trajectories, noise injection during training, or hybrid correction.

    **Resolution invariance over-claimed.** FNO transfers across resolutions for the *operator*, but a model trained only on coarse data never saw the fine-scale physics. Evaluating at high resolution produces a smooth interpolation, not new detail — and it is easy to read the smoothness as accuracy.

    **Training data cost ignored.** Generating \(N\) high-fidelity solutions is often the dominant cost of the whole project, and it is frequently omitted from speedup claims. Report it.

    **Conservation not enforced.** Neural operators do not conserve mass, momentum or energy unless constructed to. A rollout can drift in total mass with no term in the loss objecting.

    **Bulk error metrics hiding local failure.** A relative \(L_2\) error of 2% can coexist with a completely wrong shock position. Look at fields, and at error where the physics matters.

    <!-- Add your own here. -->

## Worked example

What FNO's mode truncation discards, for two solution types:

```python
import numpy as np

n = 512
x = np.linspace(0, 1, n, endpoint=False)

smooth = np.sin(2*np.pi*x) + 0.3*np.sin(6*np.pi*x)
front  = np.tanh((x - 0.5) / 0.01)

for name, f in (("smooth", smooth), ("sharp front", front)):
    spec = np.abs(np.fft.rfft(f))**2
    total = spec.sum()
    print(f"{name}:")
    for kmax in (8, 16, 32, 64):
        kept = spec[:kmax].sum() / total
        print(f"   k_max={kmax:3d}  energy retained = {100*kept:6.2f}%  "
              f"discarded = {100*(1-kept):5.2f}%")
```

```
smooth:
   k_max=  8  energy retained = 100.00%  discarded =  0.00%
   k_max= 16  energy retained = 100.00%  discarded =  0.00%
   k_max= 32  energy retained = 100.00%  discarded =  0.00%
   k_max= 64  energy retained = 100.00%  discarded =  0.00%
sharp front:
   k_max=  8  energy retained =  96.38%  discarded =  3.62%
   k_max= 16  energy retained =  98.53%  discarded =  1.47%
   k_max= 32  energy retained =  99.35%  discarded =  0.65%
   k_max= 64  energy retained =  99.69%  discarded =  0.31%
```

The smooth field is captured exactly by 8 modes. The front retains 96% of its *energy* at 8 modes and 99.7% at 64 — which sounds excellent and is misleading: the missing few percent **is** the sharpness of the front, and truncating there turns a step into a ramp. **Energy fraction is the wrong diagnostic for discontinuities**, because energy is dominated by the large scales regardless of whether the feature you care about survives.

## Connections

- [PINNs](pinns.md) — the other physics-ML route, solving one problem rather than a family.
- [Surrogates and ROM](surrogates-rom.md) — linear reduction, and the same extrapolation caveat.
- [Hybrid coupling](hybrid-coupling.md) — operators inside a solver.
- [Foundations › UQ](../foundations/uncertainty-quantification.md) — the sampling workloads that make amortisation pay.

## Sources

- Li et al. (2021), *Fourier Neural Operator for Parametric Partial Differential Equations*.
- Lu, Jin & Karniadakis (2021), *DeepONet*.
- Kovachki et al. (2023), *Neural Operator: Learning Maps Between Function Spaces*.
