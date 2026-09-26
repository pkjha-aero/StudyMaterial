---
title: Machine Learning
status: working
tags: [pillar-9, machine-learning]
---

# Machine Learning

<span class="status status-working">working</span>
<span class="pillar">pillar 9</span>

Classical ML and the craft of training models that generalize. An **active growth area**.

## Pages

| Page | Covers |
|---|---|
| [Classical machine learning](classical.md) | Bias-variance, regularised linear models, trees and boosting, SVM, clustering, PCA |
| [Training craft](training-craft.md) | Optimizers, AdamW, schedules and warmup, regularisation, debugging a model that will not learn |
| [Evaluation](evaluation.md) | Metrics under imbalance, leakage, split strategy, calibration |
| [Tabular and time series](tabular-timeseries.md) | Feature engineering, forecasting, backtesting, baselines |

## The theme

Across all four pages, the recurring failure is the same: **an evaluation that is easier than
reality**. Preprocessing fitted before the split, a rolling feature that peeks one step
ahead, accuracy quoted on 1% prevalence, a test set consulted a dozen times, a forecast
never compared against persistence.

None of these are modelling errors. Every one of them produces a *better* number, which is
why they survive review — and why the discipline in [evaluation](evaluation.md) is worth
more than any model choice.

## Connections

- [Deep Learning](../dl/index.md) — when the data is perceptual rather than tabular.
- [Scientific ML](../sciml/index.md) — ML where physics is available as structure.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — the estimation theory underneath.
