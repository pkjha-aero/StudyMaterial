---
title: Uncertainty quantification
status: solid
tags: [pillar-8, foundations, uq, monte-carlo, surrogates]
updated: 2026-09-26
---

# Uncertainty quantification

<span class="status status-solid">solid</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - Separate **aleatory** (irreducible randomness) from **epistemic** (ignorance, reducible with effort). They demand different responses and are routinely conflated.
    - Monte Carlo converges at \(1/\sqrt{N}\) **regardless of dimension** — slow, but the only method immune to the curse of dimensionality.
    - **Polynomial chaos** and stochastic collocation are far faster in low dimensions and collapse above roughly 10–20 inputs.
    - **Global sensitivity** (Sobol) apportions output variance across inputs; local derivatives answer a different and usually less interesting question.
    - **Numerical error is not uncertainty.** Verify first, then quantify — UQ on an unconverged solution measures the mesh.

## Key results

**Two kinds of uncertainty:**

<div class="result" markdown>

| | Aleatory | Epistemic |
|---|---|---|
| Source | inherent variability | lack of knowledge |
| Examples | turbulent fluctuation, manufacturing tolerance, gust | model form, unmeasured coefficient, closure choice |
| Reducible? | no | yes, with data or better models |
| Represented as | probability distribution | interval, or distribution over models |

</div>

**Monte Carlo.** For \(N\) samples of a quantity with variance \(\sigma^2\):

\[
\mathrm{SE} = \frac{\sigma}{\sqrt{N}}
\]

Independent of input dimension — the reason it survives in high dimensions. **Latin hypercube** improves stratification for the same \(N\); **quasi-Monte Carlo** (Sobol sequences) can approach \(1/N\) for smooth low-dimensional integrands.

**Polynomial chaos expansion.** Expand the output in orthogonal polynomials of the input random variables:

\[
u(\boldsymbol{\xi}) \approx \sum_{i=0}^{P} c_i \Psi_i(\boldsymbol{\xi}),
\qquad
P + 1 = \frac{(n+p)!}{n!\,p!}
\]

For \(n\) inputs at order \(p\). With \(n=5, p=3\) that is 56 terms; with \(n=20, p=3\) it is 1771 — the curse of dimensionality in one formula. Mean and variance come free from the coefficients: \(\mathbb{E}[u] = c_0\), \(\mathrm{Var}[u] = \sum_{i\ge1} c_i^2 \langle\Psi_i^2\rangle\).

**Sobol sensitivity indices.** Decompose the output variance:

\[
S_i = \frac{\mathrm{Var}_{x_i}\!\left(\mathbb{E}[y \mid x_i]\right)}{\mathrm{Var}(y)}
\quad\text{(first order)},
\qquad
S_{Ti} = 1 - \frac{\mathrm{Var}_{\mathbf{x}_{\sim i}}\!\left(\mathbb{E}[y \mid \mathbf{x}_{\sim i}]\right)}{\mathrm{Var}(y)}
\quad\text{(total)}
\]

\(S_{Ti} - S_i\) measures how much of input \(i\)'s influence comes through interactions. \(S_{Ti}\approx0\) means the input can be fixed and removed — the most valuable practical output of a UQ study.

**Gaussian process surrogate.** With kernel \(k\), the posterior at a new point is

\[
\mu_* = \mathbf{k}_*^{\mathsf T}\mathbf{K}^{-1}\mathbf{y},
\qquad
\sigma_*^2 = k_{**} - \mathbf{k}_*^{\mathsf T}\mathbf{K}^{-1}\mathbf{k}_*
\]

The variance term is what makes GPs the standard emulator: they report their own ignorance, which drives adaptive sampling and Bayesian optimization.

**Calibration.** Inferring model parameters from data, typically via Bayes. The honest version (Kennedy & O'Hagan) includes a **model discrepancy** term; without it, calibration absorbs structural model error into physical parameters and produces a well-fitting model with unphysical constants.

## Mental model

Think of the simulation as a function from inputs to outputs, and UQ as characterising that function's response to input spread. Three questions, in increasing cost: *how wide is the output distribution* (forward propagation), *which inputs drive that width* (sensitivity), and *what do observations tell me about the inputs* (inverse/calibration).

Sampling methods treat the simulation as a black box and pay in evaluations. Surrogate methods build a cheap approximation first and pay in setup and in the risk that the surrogate is wrong somewhere you did not sample.

## Numerics / practice

- **Verify before quantifying.** Grid-convergence and iterative-convergence errors must be smaller than the uncertainty you claim to measure, or you are quantifying discretization.
- **Screen first.** Morris screening or a coarse Sobol study cheaply identifies the two or three inputs that matter, making a full study affordable.
- **Report convergence of the UQ itself.** Monte Carlo estimates need their own error bars; a 100-sample mean has a visible standard error.
- **Check the surrogate out of sample**, and never trust it outside the convex hull of the training points.

??? warning "Failure modes"
    **Numerical error mistaken for uncertainty.** Running a UQ study on a mesh that is not grid-converged produces an output spread dominated by discretization error, presented as physical uncertainty. Diagnostic: repeat the study on a finer mesh — if the "uncertainty" moves, it was never uncertainty.

    **Monte Carlo convergence misjudged.** \(1/\sqrt{N}\) is slow: going from 10% to 1% error needs 100× the samples. Studies are routinely stopped at a few hundred samples with the standard error unreported, and conclusions drawn from noise.

    **PCE in too many dimensions.** The term count grows combinatorially. Beyond ~10–20 inputs a full-tensor or total-order expansion is unaffordable, and truncating it silently discards interactions. Symptom: an expansion that fits the training points and fails out of sample.

    **GP extrapolation trusted.** Outside the training data a GP reverts to the prior mean with wide variance — which is honest, provided you look at the variance. The failure is reading only \(\mu_*\). Always plot the predictive interval.

    **Calibration absorbing model error.** Fitting a turbulence constant to match one experiment gives a model that reproduces that experiment and generalises worse than before. Symptom: "calibrated" constants far outside their physically plausible range. Include a discrepancy term, or validate on held-out conditions.

    **Correlated inputs sampled independently.** Sobol indices and most sampling schemes assume independent inputs. Sampling correlated parameters independently generates physically impossible combinations, and the resulting variance decomposition is not interpretable.

    **Epistemic uncertainty forced into a probability distribution.** Assigning a uniform prior to an unknown model form makes ignorance look like quantified randomness. Interval or scenario-based treatment is often more honest.

    <!-- Add your own here. -->

## Worked example

Monte Carlo's price, and why screening comes first:

```python
import numpy as np
rng = np.random.default_rng(1)

sigma = 1.0
for N in (100, 1_000, 10_000, 100_000):
    est = rng.normal(0, sigma, N).mean()
    se  = sigma / np.sqrt(N)
    print(f"N={N:7d}   estimate={est:+.4f}   SE={se:.4f}   95% CI half-width={1.96*se:.4f}")
```

```
N=    100   estimate=-0.0736   SE=0.1000   95% CI half-width=0.1960
N=   1000   estimate=-0.0599   SE=0.0316   95% CI half-width=0.0620
N=  10000   estimate=-0.0084   SE=0.0100   95% CI half-width=0.0196
N= 100000   estimate=-0.0029   SE=0.0032   95% CI half-width=0.0062
```

Three orders of magnitude in samples buy one and a half orders in accuracy. If each sample is a CFD run, this is the entire argument for surrogates and for screening inputs before sampling them.

## Connections

- [Probability and statistics](probability-statistics.md) — estimators and the \(1/\sqrt{n}\) ceiling.
- [Verification and validation](verification-validation.md) — must come first.
- [Optimization and adjoints](optimization-adjoints.md) — cheap gradients for sensitivity.
- [Scientific ML](../sciml/index.md) — surrogates and emulators at scale.

## Sources

- Smith, *Uncertainty Quantification: Theory, Implementation, and Applications*.
- Saltelli et al., *Global Sensitivity Analysis: The Primer* — Sobol indices.
- Kennedy & O'Hagan (2001), *Bayesian calibration of computer models*.
- Rasmussen & Williams, *Gaussian Processes for Machine Learning*.
