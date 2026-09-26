---
title: Tabular and time series
status: working
tags: [pillar-9, machine-learning, time-series, forecasting, feature-engineering]
updated: 2026-09-26
---

# Tabular and time series

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - **Gradient-boosted trees are still the tabular state of the art.** Reach for deep learning only with a specific reason.
    - Feature engineering does more for tabular performance than model choice, and most of it is domain knowledge.
    - **Forecast evaluation must respect time.** Rolling-origin backtesting, never random folds.
    - **Always beat persistence first.** For many physical series, "tomorrow equals today" is a strong baseline that published models quietly fail to beat.
    - Stationarity assumptions in classical models are assumptions — check them, or use a method that does not need them.

## Key results

**Why trees win on tabular data.** Three structural reasons, from the comparative literature:

<div class="result" markdown>

1. Tabular targets are often **irregular functions** with thresholds and interactions; MLPs are biased toward smooth functions.
2. Trees are **invariant to monotone transforms** of any feature, so scale and skew do not matter.
3. Real tabular data has **uninformative features**, which trees ignore cheaply and neural nets must learn to ignore.

</div>

**Feature engineering that reliably pays:**

| Family | Examples |
|---|---|
| Domain ratios | efficiency, per-capita, normalised loads |
| Lags and differences | \(y_{t-1}\), \(\Delta y\), seasonal lags |
| Rolling statistics | mean, std, min/max over a window — **computed causally** |
| Date parts | hour, weekday, month, holiday flags |
| Cyclical encoding | \(\sin(2\pi h/24)\), \(\cos(2\pi h/24)\) for hour-of-day |
| Categorical | one-hot for low cardinality; target/ordered encoding for high |

Cyclical encoding matters more than it looks: without it, hour 23 and hour 0 are maximally distant.

**Time-series decomposition:**

\[
y_t = T_t + S_t + R_t \quad\text{(additive)},
\qquad
y_t = T_t \cdot S_t \cdot R_t \quad\text{(multiplicative)}
\]

**Classical forecasting models:**

| Model | Assumes | Good for |
|---|---|---|
| Persistence / naive | \(\hat y_{t+1} = y_t\) | **the baseline you must beat** |
| Seasonal naive | \(\hat y_{t+1} = y_{t+1-m}\) | strongly seasonal series |
| ARIMA(p,d,q) | stationarity after differencing | short series, linear dynamics |
| SARIMA | plus seasonality | classic econometric series |
| Exponential smoothing (ETS) | trend + seasonal structure | robust, fast, strong baseline |
| GBM on lag features | nothing much | multivariate, exogenous drivers |

**Backtesting.** Rolling origin: train on \([0,t]\), predict \([t+1, t+h]\), advance \(t\), repeat. Report error by horizon — one-step and ten-step accuracy are different quantities, and averaging them hides the degradation.

**Scale-free error for forecasts.** MASE compares against the in-sample naive forecast:

\[
\mathrm{MASE} = \frac{\frac{1}{h}\sum|y_t-\hat y_t|}{\frac{1}{n-m}\sum_{t=m+1}^{n}|y_t - y_{t-m}|}
\]

\(\mathrm{MASE}<1\) beats the naive forecast; \(\ge 1\) does not. It is interpretable across series in a way MAPE is not.

## Mental model

A tabular model interpolates in a space you constructed. A time-series model does the same, with the extra constraint that one axis has a direction and you may never look along it in the wrong sense.

That constraint is the whole discipline. Every rolling feature, every normalisation, every imputation must be computable from the past alone. The most common way a forecasting result turns out to be worthless is that some step in the pipeline was allowed to see forward — and the resulting scores are excellent right up until deployment.

## Numerics / practice

- **Compute rolling features with a `shift(1)`** so the current value is excluded, or the feature contains the target.
- **Report error per horizon**, plus the naive baseline on the identical split.
- **Use `TimeSeriesSplit`** or an explicit rolling loop; never `KFold`.
- **Check for regime changes** before fitting a long history. A structural break makes early data actively misleading.

??? warning "Failure modes"
    **Rolling feature without a shift.** `df.rolling(7).mean()` at time \(t\) includes \(y_t\). Used to predict \(y_t\), the feature contains one-seventh of the answer. Symptom: implausibly good one-step accuracy that vanishes at longer horizons.

    **Global statistics in a time-series pipeline.** Scaling by the full-series mean and standard deviation leaks the future into every training point. Fit scalers on the training window only, inside the backtest loop.

    **Not beating persistence.** For smooth physical series — temperature, load, pressure — persistence is strong at short horizons. A model beaten by \(\hat y_{t+1}=y_t\) has learned nothing, and this is common enough in the literature that checking it is a reflex worth having.

    **MAPE on data near zero.** The denominator explodes, so a single near-zero actual dominates the average. Also asymmetric: it penalises over-prediction more than under-prediction, quietly biasing model selection. Use MASE or RMSE.

    **Differencing without checking.** Over-differencing introduces negative autocorrelation and inflates forecast variance; under-differencing leaves a trend the model cannot represent. Test, and plot the ACF.

    **High-cardinality target encoding fitted on all rows.** Encoding a category by its mean target using the full dataset leaks the target directly. Needs out-of-fold or leave-one-out encoding, inside the CV loop.

    **Aggregating across heterogeneous series.** A single global metric over series with different scales is dominated by the largest. Report per-series, or use a scale-free metric.

    <!-- Add your own here. -->

## Worked example

Persistence as the baseline that a model has to earn its place against:

```python
import numpy as np

rng = np.random.default_rng(0)
n = 2000
t = np.arange(n)
# smooth physical-ish series: daily cycle + slow drift + noise
y = 10*np.sin(2*np.pi*t/24) + 0.002*t + rng.normal(0, 1.0, n)

naive   = y[:-1]                      # persistence: yhat(t+1) = y(t)
climate = np.full(n-1, y.mean())      # climatology: predict the mean
actual  = y[1:]

for name, pred in (("persistence", naive), ("climatology", climate)):
    mae  = np.abs(actual - pred).mean()
    rmse = np.sqrt(((actual - pred)**2).mean())
    print(f"{name:12s} MAE={mae:6.3f}  RMSE={rmse:6.3f}")
print(f"{'series std':12s} {y.std():6.3f}")
```

```
persistence  MAE= 1.933  RMSE= 2.327
climatology  MAE= 6.425  RMSE= 7.224
series std    7.222
```

Persistence achieves RMSE 2.33 against a series standard deviation of 7.22 — it already explains most of the variance. Any proposed model must be compared against 2.33, not against the standard deviation, and a paper that reports only the latter is setting a bar three times too low.

## Connections

- [Classical ML](classical.md) — the tree methods that dominate here.
- [Evaluation](evaluation.md) — split strategy and leakage.
- [Meteorology › Observations](../meteorology/observations.md) — real time series, with real pathologies.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — autocorrelation and effective sample size.

## Sources

- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* — free online, and the standard reference.
- Grinsztajn et al. (2022), *Why do tree-based models still outperform deep learning on tabular data?*
