---
title: Data assimilation
status: working
tags: [pillar-8, meteorology, inverse-problems, statistics, uncertainty]
updated: 2026-09-26
---

# Data assimilation

<span class="status status-working">working</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - DA combines a model forecast with observations, **weighted by their respective error covariances**. It is Bayesian estimation wearing a meteorological hat.
    - The background error covariance \(\mathbf{B}\) does most of the work: it spreads information from a point observation across space and between variables.
    - **4D-Var** fits a model trajectory over a window using the [adjoint](../foundations/optimization-adjoints.md); **EnKF** estimates covariances from an ensemble. Hybrids combine both.
    - Ensemble covariances are **rank-deficient and noisy**, so localization and inflation are not optional extras — they are what makes EnKF work at all.
    - Observations are not truth: they carry instrument error *and* representativeness error, and **bias must be removed** before assimilation.

## Key results

**The analysis equation.** With background \(\mathbf{x}_b\), observations \(\mathbf{y}\), observation operator \(H\):

<div class="result" markdown>

\[
\mathbf{x}_a = \mathbf{x}_b + \mathbf{K}\left(\mathbf{y} - H(\mathbf{x}_b)\right),
\qquad
\mathbf{K} = \mathbf{B}\mathbf{H}^{\mathsf T}\left(\mathbf{H}\mathbf{B}\mathbf{H}^{\mathsf T} + \mathbf{R}\right)^{-1}
\]

</div>

\(\mathbf{y} - H(\mathbf{x}_b)\) is the **innovation**, and its statistics are the primary diagnostic of whether the system is working.

**Variational form.** Minimise

\[
J(\mathbf{x}) = \underbrace{\tfrac{1}{2}(\mathbf{x}-\mathbf{x}_b)^{\mathsf T}\mathbf{B}^{-1}(\mathbf{x}-\mathbf{x}_b)}_{\text{background}}
+ \underbrace{\tfrac{1}{2}\left(\mathbf{y}-H(\mathbf{x})\right)^{\mathsf T}\mathbf{R}^{-1}\left(\mathbf{y}-H(\mathbf{x})\right)}_{\text{observations}}
\]

**4D-Var** extends this over a time window, with the model as a strong constraint:

\[
J(\mathbf{x}_0) = \tfrac{1}{2}\|\mathbf{x}_0-\mathbf{x}_b\|^2_{\mathbf{B}^{-1}}
+ \tfrac{1}{2}\sum_{i} \|\mathbf{y}_i - H_i(M_{0\to i}(\mathbf{x}_0))\|^2_{\mathbf{R}_i^{-1}}
\]

The gradient requires the adjoint of the forecast model — the same machinery as [adjoint optimization](../foundations/optimization-adjoints.md), and the reason maintaining a model adjoint is a major operational undertaking.

**Method comparison:**

| Method | \(\mathbf{B}\) | Strength | Weakness |
|---|---|---|---|
| OI / 3D-Var | static, modelled | cheap, robust | no flow dependence |
| 4D-Var | static, implicitly evolved in window | uses obs at correct time | needs adjoint; expensive |
| EnKF | ensemble-estimated, flow-dependent | no adjoint; gives an ensemble | sampling noise; needs localization |
| Hybrid / 4DEnVar | blend of static and ensemble | best of both; current operational standard | complexity |

**Ensemble Kalman filter:**

\[
\mathbf{P}^f \approx \frac{1}{N-1}\sum_{k=1}^{N}(\mathbf{x}_k - \bar{\mathbf{x}})(\mathbf{x}_k - \bar{\mathbf{x}})^{\mathsf T}
\]

With \(N \sim 50\) members and \(10^8\) state variables, \(\mathbf{P}^f\) has rank at most 49. Two fixes are mandatory:

- **Localization**: multiply covariances by a distance-decaying function (Gaspari–Cohn), removing spurious long-range correlations that are pure sampling noise.
- **Inflation**: multiplicative or additive, to counter the systematic underestimation of spread caused by sampling error and unrepresented model error.

**Observation error** \(\mathbf{R}\) includes instrument error **and representativeness error** — the mismatch between what the instrument samples (a point, a beam volume) and what the model variable means (a grid-cell average). Representativeness usually dominates for surface and radar data.

## Mental model

Two estimates of the same state, each with an uncertainty, combined in inverse-variance proportion. That is the whole idea; everything else is doing it at \(10^8\) dimensions with a nonlinear observation operator.

The covariance \(\mathbf{B}\) is the interesting object. A single radiosonde adjusts the whole surrounding analysis — in space, and across variables via balance relationships, so a temperature observation changes the wind field. That spreading *is* \(\mathbf{B}\), and whether it is static or flow-dependent is the main axis separating the methods.

## Numerics / practice

- **Monitor innovation statistics.** Mean innovation should be near zero (otherwise bias); its variance should match \(\mathbf{HBH}^{\mathsf T}+\mathbf{R}\) (otherwise the error covariances are misspecified). This is the primary health check.
- **Bias-correct satellite radiances** — variational bias correction is standard, because raw radiance biases are larger than the signal being extracted.
- **Thin dense observations** or account for correlated errors; assimilating every radar pixel as independent vastly overweights them.
- **Tune localization radius** against ensemble size: smaller ensembles need tighter localization, which in turn suppresses genuine long-range correlations.

??? warning "Failure modes"
    **Filter divergence.** The ensemble becomes overconfident, \(\mathbf{P}^f\) shrinks, observations are progressively down-weighted, and the filter stops tracking reality. Symptom: innovations growing while ensemble spread shrinks — the classic signature. Cause: sampling error plus unrepresented model error. Fix: inflation, additive noise, or a larger/better-perturbed ensemble.

    **Spurious long-range correlations.** With 50 members, sampling noise produces correlations of order \(1/\sqrt{N} \approx 0.14\) between genuinely unrelated points. Without localization a Pacific observation adjusts European temperatures. This is not subtle and it is why localization exists.

    **Correlated observation errors treated as independent.** Satellite radiances and radar data have strongly spatially correlated errors. Assuming a diagonal \(\mathbf{R}\) over-weights them by roughly the number of correlated observations. Standard mitigation is thinning — throwing away data to restore the assumption.

    **Unremoved bias.** DA theory assumes unbiased background and observations. A biased instrument pulls the analysis systematically, and because the model then forecasts from the biased analysis, the bias is self-reinforcing.

    **Representativeness error omitted from \(\mathbf{R}\).** A surface station in a valley is not a 13 km grid-cell mean. Using only instrument error makes \(\mathbf{R}\) far too small, over-fitting the analysis to unrepresentative observations and producing noisy increments.

    **Imbalanced analysis increments.** An analysis that is not in approximate geostrophic/hydrostatic balance radiates gravity waves in the first forecast hours. Symptom: noisy surface pressure and spurious precipitation early in the run. Fix: incremental analysis update, or digital filter initialisation.

    **4D-Var adjoint inconsistency.** If the adjoint does not correspond to the tangent linear of the actual nonlinear model — including its physics — the gradient is wrong and the minimisation stalls. Physics is often linearised in simplified form, which is a deliberate and documented approximation, not an accident.

    <!-- Add your own here. -->

## Worked example

Why 50 members cannot estimate a covariance without help:

```python
import numpy as np
rng = np.random.default_rng(0)

n_state, n_members = 2000, 50
truth = np.eye(n_state)                               # truly uncorrelated state

X = rng.normal(size=(n_state, n_members))
P = np.cov(X)                                          # sample covariance
off = P[~np.eye(n_state, dtype=bool)]

print(f"ensemble size          : {n_members}")
print(f"matrix rank            : {np.linalg.matrix_rank(P)} of {n_state}")
print(f"true off-diag correlation: 0")
print(f"sampled |corr| mean      : {np.abs(off).mean():.4f}")
print(f"sampled |corr| max       : {np.abs(off).max():.4f}")
print(f"expected noise ~ 1/sqrt(N): {1/np.sqrt(n_members):.4f}")
```

```
ensemble size          : 50
matrix rank            : 49 of 2000
true off-diag correlation: 0
sampled |corr| mean      : 0.1132
sampled |corr| max       : 0.8467
expected noise ~ 1/sqrt(N): 0.1414
```

Genuinely uncorrelated variables show sampled correlations up to 0.85. Every one of those is noise, and without localization the filter treats them as information.

## Connections

- [NWP](nwp.md) — DA supplies the initial conditions.
- [Observations](observations.md) — what goes into \(\mathbf{y}\), and its error structure.
- [Foundations › Optimization and adjoints](../foundations/optimization-adjoints.md) — 4D-Var is adjoint optimization.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — the estimation theory beneath it.

## Sources

- Kalnay, *Atmospheric Modeling, Data Assimilation and Predictability*.
- Evensen, *Data Assimilation: The Ensemble Kalman Filter*.
- Archive: see the [course archive](../resources/course-archive.md).
