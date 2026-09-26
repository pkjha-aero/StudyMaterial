---
title: Classical machine learning
status: working
tags: [pillar-9, machine-learning, regression, trees, svm]
updated: 2026-09-26
---

# Classical machine learning

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - **Bias–variance is the organising trade**, and every model family is a different position on it.
    - **Gradient-boosted trees remain the default for tabular data.** Deep learning has not displaced them, and the literature comparing them is consistent on this.
    - Regularisation is how you buy variance reduction with a little bias: **ridge shrinks, lasso selects**.
    - **Trees are invariant to monotone feature transforms**; linear models and distance-based methods are not. That single fact decides most preprocessing.
    - PCA is variance-maximising, not class-discriminating. It can happily discard the direction you needed.

## Key results

**The trade:**

<div class="result" markdown>

\[
\mathbb{E}\left[(y-\hat{f})^2\right] = \underbrace{\left(\mathbb{E}[\hat f]-f\right)^2}_{\text{bias}^2} + \underbrace{\mathrm{Var}(\hat f)}_{\text{variance}} + \underbrace{\sigma^2}_{\text{irreducible}}
\]

</div>

**Regularised linear models:**

\[
\text{Ridge:}\ \min_\beta \|y-X\beta\|^2 + \lambda\|\beta\|_2^2,
\qquad
\text{Lasso:}\ \min_\beta \|y-X\beta\|^2 + \lambda\|\beta\|_1
\]

Ridge shrinks all coefficients smoothly and handles collinearity; lasso drives some to exactly zero, giving selection. Elastic net blends them and is the safer default when predictors are correlated — lasso picks one of a correlated group arbitrarily.

**Trees and ensembles:**

| Method | Idea | Strength | Weakness |
|---|---|---|---|
| Decision tree | recursive axis-aligned splits | interpretable | high variance |
| Random forest | bagging + feature subsampling | robust, few knobs | less accurate than boosting |
| Gradient boosting | sequential fit to residuals | best-in-class tabular | needs tuning, can overfit |
| XGBoost / LightGBM / CatBoost | engineered GBMs | fast, handle missing values | many hyperparameters |

Boosting minimises a loss by stage-wise additive fitting:

\[
F_m(x) = F_{m-1}(x) + \nu\, h_m(x),
\qquad
h_m \approx -\left.\frac{\partial L}{\partial F}\right|_{F_{m-1}}
\]

Learning rate \(\nu\) and number of trees trade off directly — halve \(\nu\), roughly double the trees.

**SVM.** Maximum-margin separation, with the kernel trick giving nonlinear boundaries without explicit feature maps:

\[
\min_{w,b}\ \tfrac{1}{2}\|w\|^2 + C\sum_i \xi_i,
\qquad
K(x,x') = \exp\left(-\gamma\|x-x'\|^2\right)
\]

\(C\) controls the margin/violation trade; \(\gamma\) the kernel width. Both need scaling of the inputs, and SVM scales poorly past ~10⁵ samples.

**Unsupervised:**

- **k-means** minimises within-cluster variance; assumes spherical, similarly-sized clusters, and \(k\) must be chosen.
- **DBSCAN** finds density-connected clusters of arbitrary shape and labels outliers; sensitive to `eps`.
- **PCA** projects onto directions of maximum variance via the SVD of the centred data.
- **UMAP / t-SNE** are visualisation tools. Distances between clusters in the embedding are not meaningful.

## Mental model

Every supervised method is answering "how should I interpolate between the training points?", and the differences are in the assumed shape of the answer. Linear models assume a plane. Trees assume axis-aligned boxes. Kernel methods assume smoothness at a chosen length scale. Nearest neighbours assume the answer is locally constant.

Choosing a model is choosing which of those assumptions least offends your data. When the relationship really is a smooth function of a few variables, a linear or kernel model wins on data efficiency. When it is a pile of interacting thresholds — which is what most tabular business and engineering data looks like — trees win.

## Numerics / practice

- **Scale for anything distance- or gradient-based** (SVM, kNN, linear with regularisation, neural nets). Do not bother for trees.
- **Fit the scaler inside the cross-validation fold**, not before splitting — otherwise test statistics leak into training.
- **Start with a gradient-boosted baseline** on tabular problems and only move on if it is genuinely insufficient.
- **Use `scikit-learn` pipelines** so preprocessing travels with the model and cannot be applied inconsistently at inference.

??? warning "Failure modes"
    **Preprocessing fitted before the split.** `StandardScaler().fit(X)` on the whole dataset before cross-validation leaks the test distribution into training. The effect is small for scaling and large for imputation or target encoding — and it always makes validation scores optimistic. Use a `Pipeline`.

    **Lasso with correlated predictors.** Lasso arbitrarily selects one of a correlated group and zeroes the rest. Rerun on a bootstrap sample and it picks a different one. Reading the selected set as "the important variables" is then unsupported. Elastic net is more stable.

    **PCA before classification, uncritically.** PCA maximises variance without reference to the label. If the discriminative direction happens to be low-variance — common when one feature has a large scale — PCA discards exactly what you needed. LDA or supervised feature selection is the right tool when the goal is discrimination.

    **Reading t-SNE / UMAP geometry.** Cluster sizes, inter-cluster distances and density in these embeddings are artefacts of the algorithm and its perplexity or neighbour count. They are for looking at, not for measuring.

    **Tree feature importance read as causal.** Impurity-based importance is biased towards high-cardinality and continuous features, and correlated features split the credit arbitrarily. Permutation importance on held-out data is better; neither is causal.

    **Extrapolating a tree model.** Trees predict a constant outside the range of the training data — the value of the boundary leaf. Feed them an input beyond anything seen and the prediction flatlines, silently and confidently.

    **k-means with \(k\) from the elbow only.** The elbow is often ambiguous. Silhouette, gap statistic, or a downstream task metric are all more defensible, and "the clusters are not well separated" is a valid finding.

    <!-- Add your own here. -->

## Worked example

Feature selection outside the cross-validation loop, on data containing **no signal at
all**:

```python
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, KFold
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))        # pure noise
y = rng.integers(0, 2, 100)             # random labels

cv = KFold(5, shuffle=True, random_state=0)

# WRONG: pick the 20 best features using every row, then cross-validate
X_sel = SelectKBest(f_classif, k=20).fit_transform(X, y)
leaked = cross_val_score(LogisticRegression(max_iter=1000), X_sel, y, cv=cv)

# RIGHT: selection refit inside each fold
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
clean = cross_val_score(pipe, X, y, cv=cv)

print(f"leaked selection   : {leaked.mean():.3f}")
print(f"pipeline (correct) : {clean.mean():.3f}")
```

```
leaked selection   : 0.850
pipeline (correct) : 0.460
```

85% accuracy on random labels. With 5,000 noise features and 100 samples, some features
correlate with the labels by chance; selecting them using the whole dataset carries that
chance correlation into every fold. The pipeline version correctly reports chance.

Scaling leaks far less than this — often nothing measurable. The mechanism is identical;
what changes is how much the preprocessing step depends on the labels.

## Connections

- [Evaluation](evaluation.md) — cross-validation done properly, and metrics.
- [Training craft](training-craft.md) — the gradient-based side.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — estimators and model selection.
- [Tabular and time series](tabular-timeseries.md) — where these methods are still state of the art.

## Sources

- Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning*.
- Murphy, *Probabilistic Machine Learning*.
- Grinsztajn et al. (2022), *Why do tree-based models still outperform deep learning on tabular data?*
