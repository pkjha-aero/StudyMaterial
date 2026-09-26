---
title: Evaluation
status: working
tags: [pillar-9, machine-learning, metrics, leakage, calibration]
updated: 2026-09-26
---

# Evaluation

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - **Leakage is the dominant failure mode in applied ML**, and it always makes results look better. A suspiciously good score is a leakage hypothesis.
    - **Accuracy is useless under class imbalance.** At 1% positives, predicting "negative" scores 99%.
    - **The split must respect the structure of the data** — time, groups, subjects. Random \(k\)-fold on a time series is leakage.
    - **A well-ranked model can be badly calibrated.** AUC says nothing about whether "0.8" means 80%.
    - The test set is spent the first time you use it to make a decision.

## Key results

**Confusion-matrix metrics:**

<div class="result" markdown>

\[
\text{Precision} = \frac{TP}{TP+FP},
\qquad
\text{Recall} = \frac{TP}{TP+FN},
\qquad
F_1 = \frac{2\,PR}{P+R}
\]

</div>

| Metric | Answers | Use when |
|---|---|---|
| Accuracy | fraction correct | balanced classes, equal costs |
| Precision | of flagged, how many are real | false positives are expensive |
| Recall | of real, how many were found | false negatives are expensive |
| F1 | harmonic mean | you must have one number |
| ROC-AUC | ranking quality across thresholds | balanced-ish; threshold-free comparison |
| PR-AUC | ranking quality on the positive class | **imbalanced data** |
| Log loss / Brier | probability quality | you need calibrated probabilities |

**ROC vs PR under imbalance.** ROC-AUC uses the false-positive *rate*, whose denominator is the (huge) negative count, so it stays flattering when positives are rare. PR-AUC uses precision, whose denominator is the number of predicted positives, so it degrades honestly. At 1% prevalence a model can show ROC-AUC 0.95 and PR-AUC 0.3.

**Calibration.** A model is calibrated if, among samples predicted \(p\), a fraction \(p\) are positive:

\[
\text{ECE} = \sum_{b=1}^{B}\frac{n_b}{N}\left|\text{acc}(b) - \text{conf}(b)\right|
\]

Modern deep networks are systematically **over**-confident. Platt scaling and isotonic regression fix it post hoc; temperature scaling (one parameter, fit on validation) is the standard cheap option.

**Cross-validation strategy — match it to the dependence structure:**

| Data structure | Correct split |
|---|---|
| i.i.d. samples | random \(k\)-fold |
| Class imbalance | stratified \(k\)-fold |
| Repeated subjects / sites / patients | **grouped** \(k\)-fold |
| Time series | forward-chaining / rolling origin |
| Spatial fields | blocked spatial CV |

**Regression metrics.** RMSE penalises large errors and shares the target's units; MAE is robust to outliers; \(R^2\) is scale-free but can be negative and is easy to inflate with a large-variance test set. MAPE breaks near zero targets. Report at least two, and always report the target's own spread for reference.

## Mental model

An evaluation is a simulation of deployment. Every way in which the split differs from how the model will actually be used is a way the estimate can be optimistic.

That framing answers most questions directly. Will the model see future data? Then split by time. Will it see new patients? Then split by patient. Will it see a different site? Then hold out a site. If your split does not mirror the deployment gap, your number does not measure what you want.

## Numerics / practice

- **Establish a baseline first.** Majority class, or persistence for time series. A model that does not beat it has nothing to report.
- **Report an uncertainty on the metric** — across folds, or by bootstrap. A single number on one split invites over-reading.
- **Plot a calibration curve** whenever probabilities will be used for a decision or a threshold.
- **Choose the threshold on validation data**, optimising the quantity you actually care about — not 0.5 by default.

??? warning "Failure modes"
    **Target leakage through a feature.** A feature computed after, or derived from, the outcome. Classic examples: a "number of treatments" field that only exists for diagnosed patients; a timestamp that differs for positive cases. Symptom: near-perfect validation score that collapses in production. Diagnostic: if a single feature carries most of the signal, examine how it is populated.

    **Temporal leakage.** Random \(k\)-fold on a time series trains on the future to predict the past. Symptom: excellent CV and useless live performance. Also occurs subtly via features built from full-series statistics (a global mean, a resampled rolling window).

    **Group leakage.** The same patient, site, or physical object appearing in both train and test. The model memorises the entity rather than the pattern. Use `GroupKFold`.

    **Accuracy on imbalanced data.** At 1% prevalence, the all-negative classifier gets 99%. Reporting accuracy here is not merely uninformative, it actively hides that the model learned nothing.

    **ROC-AUC on heavily imbalanced data.** Stays high when the model is practically useless because false-positive rate has an enormous denominator. Use PR-AUC, and state the prevalence — PR-AUC's baseline *is* the prevalence, so the number is uninterpretable without it.

    **Test set reused.** Every decision made by looking at test performance — model choice, threshold, feature set, an early-stopping epoch — transfers information from test to model. After a few rounds it is a validation set with an optimistic bias. Hold out a final test set and touch it once.

    **Confusing ranking with probability.** A model can rank perfectly (AUC 1.0) while every predicted probability is wrong. If a downstream decision uses the number rather than the order, calibration is what matters.

    <!-- Add your own here. -->

## Worked example

Why the metric choice, not the model, decides the story under imbalance:

```python
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score

rng = np.random.default_rng(0)
n, prevalence = 20_000, 0.01
y = (rng.random(n) < prevalence).astype(int)

# a mediocre but real signal
score = rng.normal(0, 1, n) + 1.2 * y

print(f"prevalence           : {y.mean():.3%}")
print(f"accuracy, all-negative: {accuracy_score(y, np.zeros(n)):.4f}")
print(f"ROC-AUC              : {roc_auc_score(y, score):.4f}")
print(f"PR-AUC               : {average_precision_score(y, score):.4f}")
print(f"PR-AUC baseline      : {y.mean():.4f}")
```

```
prevalence           : 0.985%
accuracy, all-negative: 0.9901
ROC-AUC              : 0.7854
PR-AUC               : 0.0553
PR-AUC baseline      : 0.0098
```

Accuracy says 99% — from a model that predicts nothing at all. ROC-AUC says 0.79, which sounds respectable. PR-AUC says 0.055 against a baseline of 0.0098: real signal, about five times better than chance, and nowhere near deployable. Only the last pair tells you that.

## Connections

- [Classical ML](classical.md) — pipelines that prevent preprocessing leakage.
- [Training craft](training-craft.md) — validation loss during training.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — effective sample size, multiple comparisons.
- [Foundations › V&V](../foundations/verification-validation.md) — the same discipline in a simulation context.

## Sources

- Kaufman et al. (2012), *Leakage in data mining*.
- Guo et al. (2017), *On calibration of modern neural networks*.
- Saito & Rehmsmeier (2015), *The precision-recall plot is more informative than the ROC plot*.
