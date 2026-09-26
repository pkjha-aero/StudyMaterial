---
title: Probability and statistics
status: solid
tags: [pillar-8, foundations, statistics, inference, regression]
updated: 2026-09-26
---

# Probability and statistics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - An estimator has **bias** and **variance**; reducing one usually raises the other, and the useful target is mean squared error.
    - The \(1/\sqrt{n}\) convergence of the sample mean is the ceiling on almost everything — and it assumes **independent** samples.
    - Simulation and time-series data are **autocorrelated**, so the effective sample size is far below the number of points. This is the single biggest source of overconfident error bars in computational work.
    - Bayes gives a posterior distribution; frequentist methods give procedures with coverage guarantees. Both are useful; mixing their interpretations is not.
    - **Model selection** must penalise complexity, or you fit noise.

## Key results

**Estimator quality.** For an estimator \(\hat{\theta}\):

<div class="result" markdown>

\[
\mathrm{MSE}(\hat{\theta}) = \underbrace{\left(\mathbb{E}[\hat{\theta}]-\theta\right)^2}_{\text{bias}^2} + \underbrace{\mathrm{Var}(\hat{\theta})}_{\text{variance}}
\]

</div>

**Central limit theorem.** For i.i.d. samples with finite variance,

\[
\bar{X}_n \xrightarrow{d} \mathcal{N}\!\left(\mu, \frac{\sigma^2}{n}\right),
\qquad
\mathrm{SE} = \frac{\sigma}{\sqrt{n}}
\]

Halving the error costs four times the samples — the fundamental economics of Monte Carlo and of averaging turbulence statistics.

**Effective sample size.** For an autocorrelated series with integrated autocorrelation time \(\tau\):

\[
n_{\text{eff}} = \frac{n}{1 + 2\tau},
\qquad
\mathrm{SE} = \frac{\sigma}{\sqrt{n_{\text{eff}}}}
\]

A CFD time series sampled every step can easily have \(\tau \sim 10^3\) steps, so \(10^6\) samples carry the information of about \(500\). Using \(\sigma/\sqrt{n}\) understates the error by a factor of ~45.

**Bayes' theorem:**

\[
p(\theta \mid D) = \frac{p(D \mid \theta)\,p(\theta)}{p(D)}
\qquad
\text{posterior} \propto \text{likelihood} \times \text{prior}
\]

**Linear least squares.** For \(\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\varepsilon}\), \(\boldsymbol{\varepsilon}\sim\mathcal{N}(0,\sigma^2\mathbf{I})\):

\[
\hat{\boldsymbol{\beta}} = (\mathbf{X}^{\mathsf T}\mathbf{X})^{-1}\mathbf{X}^{\mathsf T}\mathbf{y},
\qquad
\mathrm{Cov}(\hat{\boldsymbol{\beta}}) = \sigma^2 (\mathbf{X}^{\mathsf T}\mathbf{X})^{-1}
\]

Compute it by QR or SVD, never by forming \(\mathbf{X}^{\mathsf T}\mathbf{X}\) — see [math methods](math-methods.md).

**Model selection**, lower is better:

\[
\mathrm{AIC} = 2k - 2\ln\hat{L},
\qquad
\mathrm{BIC} = k\ln n - 2\ln\hat{L}
\]

BIC penalises complexity harder and is consistent for model identification; AIC targets predictive accuracy. Cross-validation is more robust than either and costs more.

**What a 95% confidence interval means.** If the procedure were repeated many times, 95% of the intervals produced would contain the true value. It does *not* mean there is a 95% probability the parameter is in this particular interval — that is the credible interval, and it requires a prior.

## Mental model

Almost every statistical question in computational work reduces to: *how much independent information do I actually have?* Not how many numbers were written to disk. A long correlated run, a fine mesh with smooth fields, an ensemble with shared initial conditions — all have far less information than their size suggests.

The bias–variance split is the other recurring frame. A coarse model is biased but stable; a flexible one is unbiased but noisy. Every choice of turbulence closure, polynomial order, or regression basis is a position on that trade.

## Numerics / practice

- **Estimate \(\tau\)** before quoting any error bar on a time series — from the autocorrelation function, or by batch means (split into blocks, use the variance of block means).
- **Report the averaging window** in physical units and in integral timescales.
- **Plot the data** before fitting. Anscombe's quartet exists because summary statistics hide structure.
- **Hold out a test set** and touch it once. Repeated evaluation turns it into a training set.

??? warning "Failure modes"
    **Treating correlated samples as independent.** The dominant error in simulation statistics. Symptom: error bars that shrink smoothly as the run lengthens but do not overlap between two independent runs of the same case. That mismatch is the diagnostic — if independent repeats disagree by more than their stated uncertainty, \(\tau\) was ignored.

    **Confidence interval read as probability about the parameter.** The frequentist interval makes a statement about the procedure. Reporting "there is a 95% chance the drag is in this range" from a frequentist CI is a category error — harmless in conversation, misleading in a report.

    **Multiple comparisons.** Test twenty hypotheses at \(p<0.05\) and expect one false positive by construction. Common in parameter sweeps: run 50 configurations, report the one that "significantly" improved. Correct for it (Bonferroni, FDR) or pre-register the comparison.

    **p-value as effect size.** A tiny \(p\) on a huge sample can accompany a physically irrelevant difference. Report the effect and its interval, not just significance.

    **Extrapolating a fit.** Regression is interpolation between the data you had. A polynomial fit is especially violent outside its range — high-order fits diverge immediately past the last point.

    **Overfitting via model selection on the same data.** Choosing the model by test-set performance and then reporting that performance is optimistic. Needs a third split, or nested cross-validation.

    **Assuming normality for extremes.** The CLT governs the *mean*, not the tails. Peak loads, gusts and extreme events are tail questions, and Gaussian tails understate them badly.

    <!-- Add your own here. -->

## Worked example

What autocorrelation does to an error bar:

```python
import numpy as np
rng = np.random.default_rng(0)

n, phi = 100_000, 0.99                      # AR(1) process
x = np.zeros(n)
for i in range(1, n):
    x[i] = phi * x[i-1] + rng.normal()

tau  = phi / (1 - phi)                      # integrated autocorrelation time
neff = n / (1 + 2 * tau)
sd   = x.std(ddof=1)
print(f"naive SE  = {sd/np.sqrt(n):.4f}   (assumes {n} independent samples)")
print(f"correct SE= {sd/np.sqrt(neff):.4f}   (n_eff = {neff:.0f})")
print(f"understated by {np.sqrt(n/neff):.0f}x")
```

```
naive SE  = 0.0228   (assumes 100000 independent samples)
correct SE= 0.3220   (n_eff = 503)
understated by 14x
```

A hundred thousand samples carrying the information of five hundred. The naive error bar is fourteen times too small.

## Connections

- [Uncertainty quantification](uncertainty-quantification.md) — propagating and decomposing this uncertainty.
- [Mathematical methods](math-methods.md) — least squares conditioning.
- [Turbulence](../fluids/turbulence/index.md) — where averaging times actually bite.
- [ML › Evaluation](../ml/index.md) — the same ideas in a modelling context.

## Sources

- Wasserman, *All of Statistics* — compact and rigorous.
- Gelman et al., *Bayesian Data Analysis*.
- Archive: see the [course archive](../resources/course-archive.md).
