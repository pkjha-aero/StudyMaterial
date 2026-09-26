---
title: Training craft
status: working
tags: [pillar-9, machine-learning, optimizers, regularization, debugging]
updated: 2026-09-26
---

# Training craft

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - **Learning rate is the hyperparameter that matters most.** Get it wrong and nothing else you tune will help.
    - **AdamW, not Adam,** when you want weight decay: Adam's L2 penalty interacts with the adaptive scaling and is not the same thing.
    - Warmup plus cosine decay is the default schedule for a reason — it stabilises the high-variance early steps.
    - **Overfit a single batch first.** If a model cannot drive the loss to zero on ten examples, the bug is in the code, not the data.
    - Batch size and learning rate are coupled; changing one without the other changes the effective optimisation problem.

## Key results

**Optimizers:**

<div class="result" markdown>

\[
\text{SGD+momentum:}\quad v_{t} = \mu v_{t-1} + g_t,\qquad \theta_{t+1} = \theta_t - \eta v_t
\]

\[
\text{Adam:}\quad m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t,\quad
v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2,\quad
\theta_{t+1} = \theta_t - \eta\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}
\]

</div>

**AdamW** decouples weight decay from the adaptive step:

\[
\theta_{t+1} = \theta_t - \eta\left(\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon} + \lambda\theta_t\right)
\]

In plain Adam, an L2 term enters \(g_t\) and is then divided by \(\sqrt{\hat v_t}\), so parameters with large gradients get *less* decay — the opposite of the intent. This is why AdamW is the default in essentially all modern training code.

| Optimizer | Typical LR | Use |
|---|---|---|
| SGD + momentum | \(10^{-2}\)–\(10^{-1}\) | CNNs on vision, where it often generalises best |
| AdamW | \(10^{-4}\)–\(10^{-3}\) | transformers, and most things |
| AdamW (fine-tuning) | \(10^{-5}\)–\(10^{-4}\) | pretrained weights |

**Schedules.** Linear warmup over a few hundred to a few thousand steps, then cosine decay:

\[
\eta_t = \eta_{\max}\cdot\frac{t}{T_w} \ (t<T_w),
\qquad
\eta_t = \eta_{\min} + \tfrac{1}{2}(\eta_{\max}-\eta_{\min})\left(1+\cos\frac{\pi(t-T_w)}{T-T_w}\right)
\]

Warmup matters because Adam's second-moment estimate is noisy in the first steps, so the effective step size is erratic exactly when the model is most fragile.

**Batch size / learning rate scaling.** For SGD, the linear scaling rule: multiply batch size by \(k\), multiply LR by \(k\). For Adam, \(\sqrt{k}\) is the better heuristic. Neither holds at extreme batch sizes.

**Regularisation:**

| Method | Effect |
|---|---|
| Weight decay | shrinks weights; \(10^{-2}\) typical for AdamW transformers |
| Dropout | random unit masking; less used in transformers than in older CNNs |
| Label smoothing | softens targets, calibrates confidence, usually \(\epsilon=0.1\) |
| Early stopping | implicit regularisation via limited optimisation |
| Data augmentation | usually the strongest of all, and the most domain-specific |

**Normalisation.** BatchNorm normalises across the batch (so it behaves differently in train and eval, and badly at small batch size); LayerNorm normalises across features per sample, which is why transformers use it. Pre-norm placement (norm before the sublayer) trains more stably at depth than post-norm.

## Mental model

Training is a search, and the learning rate is the step length. Too large and you bounce out of every basin you find; too small and you never leave the first one within your compute budget. Everything else — schedules, warmup, momentum, adaptivity — is machinery for making a good step length possible at different points in the search.

Regularisation is a statement about what you believe the answer looks like. Weight decay says "small weights are more likely". Augmentation says "these transformations should not change the label". The second is a much stronger and more useful prior when you can express it, which is why augmentation usually beats generic regularisers.

## Numerics / practice

- **Run an LR range test** before a long training run: sweep LR upward over a few hundred steps and plot loss. Take roughly an order of magnitude below the divergence point.
- **Log gradient norms.** A sudden spike precedes most loss explosions, and gradient clipping at a fixed norm (1.0 is a common default) turns a crash into a bump.
- **Fix all seeds and log them**, and be aware GPU reductions are still nondeterministic unless you force deterministic kernels — see [research craft](../foundations/research-craft.md).
- **Mixed precision** (bf16 preferred over fp16 — much wider dynamic range and no loss scaling needed) is close to free on modern hardware.

??? warning "Failure modes"
    **Learning rate an order of magnitude off.** Too high gives a loss that spikes, plateaus high, or goes NaN; too low gives a loss that decreases smoothly and far too slowly, which is more insidious because it looks like training is working. The LR range test costs minutes and removes the ambiguity.

    **Adam with L2 instead of AdamW.** `Adam(weight_decay=...)` in older frameworks applies L2 inside the gradient, where the adaptive denominator distorts it. Symptom: weight decay appears to do almost nothing, or hurts. Use AdamW.

    **No warmup with Adam.** The second-moment estimate is built from very few samples in the first steps, so \(\sqrt{\hat v_t}\) is unreliable and steps can be enormous. Symptom: loss spikes in the first hundred steps and the run never recovers its best trajectory.

    **BatchNorm at small batch size.** Batch statistics from 2–4 samples are noisy, and train/eval behaviour diverges. Symptom: good training loss, poor eval loss, with the gap closing if you raise batch size. GroupNorm or LayerNorm is the fix.

    **Not overfitting a single batch first.** The cheapest possible test: take 8–16 examples and train until the loss is essentially zero. If it cannot, you have a bug — a detached gradient, a wrong loss reduction, a label misalignment — and no amount of data or tuning will fix it. Skipping this step is the most common reason people debug the wrong thing for a day.

    **Augmentation applied to the validation set.** Random crops and flips at eval time make validation noisy and pessimistic. Related and worse: normalisation statistics computed from the validation set.

    **Gradient accumulation without scaling the loss.** Accumulating over \(k\) micro-batches without dividing the loss by \(k\) multiplies the effective learning rate by \(k\). Symptom: a configuration that worked at batch size 32 diverges when "the same" batch size is reached by accumulation.

    <!-- Add your own here. -->

## Worked example

Why Adam needs warmup, in the behaviour of its own step size:

```python
import numpy as np

beta2, eps, lr = 0.999, 1e-8, 1e-3
g = 0.1                                  # steady gradient
v = 0.0

print(" step   v_hat      effective step")
for t in range(1, 9):
    v = beta2 * v + (1 - beta2) * g**2
    v_hat = v / (1 - beta2**t)           # bias correction
    step = lr * g / (np.sqrt(v_hat) + eps)
    print(f"{t:5d}   {v_hat:.6f}   {step:.6f}")
```

```
 step   v_hat      effective step
    1   0.010000   0.001000
    2   0.010000   0.001000
    3   0.010000   0.001000
    4   0.010000   0.001000
    5   0.010000   0.001000
    6   0.010000   0.001000
    7   0.010000   0.001000
    8   0.010000   0.001000
```

With a *constant* gradient, bias correction works perfectly and the step is stable — which is the point. The instability comes from gradient *variance*: early in training the per-step gradients differ wildly, \(\hat v_t\) is estimated from a handful of them, and the step size swings by orders of magnitude between steps. Warmup caps the damage until the estimate settles.

## Connections

- [Classical ML](classical.md) — the non-gradient alternatives.
- [Evaluation](evaluation.md) — knowing whether any of this helped.
- [DL › PyTorch patterns](../dl/pytorch-patterns.md) — the implementation side.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — optimisation in the deterministic setting.

## Sources

- Loshchilov & Hutter (2019), *Decoupled Weight Decay Regularization* — AdamW.
- Goodfellow, Bengio & Courville, *Deep Learning*, ch. 8.
- Karpathy, *A Recipe for Training Neural Networks*.
